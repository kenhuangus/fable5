import os
import requests

API_KEY = os.environ["BILLING_API_KEY"]  # static, long-lived


def charge_customer(customer_id, amount_cents):
    return requests.post(
        "https://billing.internal/charge",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"customer_id": customer_id, "amount_cents": amount_cents},
    )
