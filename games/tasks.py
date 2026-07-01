from celery import shared_task
import requests
import json
import hmac
import hashlib

from .models import WebhookDeliveryLog


@shared_task(bind=True, max_retries=3)
def send_webhook_task(
    self,
    log_id,
    webhook_url,
    webhook_secret,
    payload
):
    try:

        body = json.dumps(
            payload,
            sort_keys=True
        ).encode("utf-8")

        signature = hmac.new(
            webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Signature": f"sha256={signature}",
        }

        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=5,
        )

        log = WebhookDeliveryLog.objects.get(id=log_id)

        log.response_code = response.status_code
        log.response_body = response.text

        if response.status_code == 200:
            log.status = "success"
        else:
            log.status = "failed"

        log.attempts += 1

        log.save()

    except Exception as exc:

        log = WebhookDeliveryLog.objects.get(id=log_id)

        log.status = "failed"

        log.attempts += 1

        log.save()

        raise self.retry(exc=exc, countdown=60)