import hmac
import hashlib
import json
import requests


def send_expiry_webhook(publisher, game_key_str, game_title, expired_at):
    payload = {
        "event": "game_key.expired",
        "game_key": game_key_str,
        "game_title": game_title,
        "expired_at": expired_at.isoformat(),
    }

    secret = publisher.webhook_secret.encode("utf-8")

    body = json.dumps(payload, sort_keys=True).encode("utf-8")

    signature = hmac.new(
        secret,
        body,
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Signature": f"sha256={signature}",
    }

    try:
        response = requests.post(
            publisher.webhook_url,
            json=payload,
            headers=headers,
            timeout=5,
        )

        response.raise_for_status()

    except Exception as e:
        print(f"[Webhook] Delivery failed for publisher {publisher.id}: {e}")