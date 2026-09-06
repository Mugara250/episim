"""Dev-only mail sender: relays through Mailhog (or any log-only SMTP
catcher) so verification/reset emails are inspectable at localhost:8025
instead of actually being delivered.
"""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=5) as smtp:
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
    except OSError:
        logger.warning("Could not reach SMTP server, logging email instead:\nTo: %s\nSubject: %s\n%s", to, subject, body)
