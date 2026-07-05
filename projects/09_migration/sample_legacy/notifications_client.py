import os
import requests

NOTIFY_KEY = os.environ["NOTIFY_API_KEY"]  # static, long-lived


def send_email(to, subject, body):
    return requests.post(
        "https://notify.internal/send",
        headers={"Authorization": f"Bearer {NOTIFY_KEY}"},
        json={"to": to, "subject": subject, "body": body},
    )
