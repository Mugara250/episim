"""Thin S3/MinIO wrapper for uploaded files (e.g. population dataset imports).

The API endpoint stores the raw upload here and hands the object key to a
Celery task; the worker streams it back down for chunked parsing. Works
against MinIO locally and real S3 in production with no code change.
"""
from functools import lru_cache

import boto3
from botocore.client import Config

from app.core.config import settings


@lru_cache
def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_root_user,
        aws_secret_access_key=settings.minio_root_password,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def _ensure_bucket() -> None:
    client = _client()
    try:
        client.head_bucket(Bucket=settings.minio_bucket)
    except Exception:
        client.create_bucket(Bucket=settings.minio_bucket)


def put_object(key: str, data: bytes) -> str:
    _ensure_bucket()
    _client().put_object(Bucket=settings.minio_bucket, Key=key, Body=data)
    return key


def get_object(key: str) -> bytes:
    return _client().get_object(Bucket=settings.minio_bucket, Key=key)["Body"].read()


def delete_object(key: str) -> None:
    try:
        _client().delete_object(Bucket=settings.minio_bucket, Key=key)
    except Exception:
        pass
