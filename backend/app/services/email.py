"""Mail sender. In dev it relays through Mailhog (or any log-only SMTP
catcher) so verification/reset emails are inspectable at localhost:8025; in
production, point SMTP_* at a real provider and set SMTP_SECURITY.
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

    smtp_class = smtplib.SMTP_SSL if settings.smtp_security == "ssl" else smtplib.SMTP
    try:
        with smtp_class(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_security == "starttls":
                smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
    except OSError:
        if settings.is_production:
            # Don't write the body (it holds verify/reset tokens) to production logs.
            logger.exception("Failed to send email to %s (subject: %s)", to, subject)
        else:
            logger.warning("Could not reach SMTP server, logging email instead:\nTo: %s\nSubject: %s\n%s", to, subject, body)
