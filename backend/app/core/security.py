"""Small security helpers that don't need a dedicated dependency.

TOTP (RFC 6238) is hand-rolled on top of stdlib `hmac`/`hashlib` rather than
pulling in `pyotp`, since the project's dependency set is fixed. The MFA
secret "encryption" is a stdlib-only reversible cipher derived from
JWT_SECRET — good enough for a local prototype, but a real deployment should
swap it for a KMS-backed envelope encryption without touching callers.
"""

import base64
import hashlib
import hmac
import os
import secrets
import struct
import time

from app.core.config import settings


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def generate_raw_token() -> str:
    return secrets.token_urlsafe(32)


def _xor_stream(data: bytes, key: bytes) -> bytes:
    stream = bytearray()
    counter = 0
    while len(stream) < len(data):
        stream.extend(hashlib.sha256(key + counter.to_bytes(4, "big")).digest())
        counter += 1
    return bytes(b ^ k for b, k in zip(data, stream))


def encrypt_secret(plaintext: str) -> str:
    key = hashlib.sha256(settings.jwt_secret.encode()).digest()
    nonce = os.urandom(16)
    cipher = _xor_stream(plaintext.encode(), key + nonce)
    return base64.urlsafe_b64encode(nonce + cipher).decode()


def decrypt_secret(token: str) -> str:
    raw = base64.urlsafe_b64decode(token.encode())
    nonce, cipher = raw[:16], raw[16:]
    key = hashlib.sha256(settings.jwt_secret.encode()).digest()
    plain = _xor_stream(cipher, key + nonce)
    return plain.decode()


def generate_totp_secret() -> str:
    return base64.b32encode(os.urandom(20)).decode("utf-8").rstrip("=")


def get_totp_uri(secret: str, email: str, issuer: str = "EpiSim") -> str:
    return f"otpauth://totp/{issuer}:{email}?secret={secret}&issuer={issuer}&digits=6&period=30"


def _totp_at(secret: str, for_time: int, digits: int = 6, period: int = 30) -> str:
    padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(padded.upper())
    counter = struct.pack(">Q", for_time // period)
    digest = hmac.new(key, counter, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**digits)
    return str(code_int).zfill(digits)


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    now = int(time.time())
    period = 30
    for offset in range(-window, window + 1):
        if hmac.compare_digest(_totp_at(secret, now + offset * period), code):
            return True
    return False
