import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")


def send_email_notification(to_email: str, subject: str, body: str) -> bool:
    if not SENDGRID_API_KEY or not SENDGRID_FROM_EMAIL:
        return False

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": SENDGRID_FROM_EMAIL},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
    except requests.RequestException as exc:
        logging.warning("SendGrid request exception: %s", exc)
        return False

    if response.status_code not in {200, 202}:
        logging.warning(
            "SendGrid request failed: status=%s body=%s",
            response.status_code,
            response.text[:200],
        )
        return False

    return True
