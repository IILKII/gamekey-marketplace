from django.core.management.base import BaseCommand
from django.utils import timezone

from games.models import GameKey, WebhookDeliveryLog
from games.tasks import send_webhook_task


class Command(BaseCommand):
    help = "Mark expired keys and queue webhook deliveries."

    def handle(self, *args, **options):

        expired_keys = GameKey.objects.select_related(
            "game__publisher"
        ).filter(
            expires_at__lte=timezone.now(),
            status="active",
        )

        count = 0

        for key in expired_keys:

            key.status = "expired"
            key.save()

            payload = {
                "event": "game_key.expired",
                "game_key": key.key_string,
                "game_title": key.game.title,
                "expired_at": key.expires_at.isoformat(),
            }

            log = WebhookDeliveryLog.objects.create(
                publisher=key.game.publisher,
                game_key=key,
                event="game_key.expired",
                status="pending",
            )

            send_webhook_task.delay(
                log.id,
                key.game.publisher.webhook_url,
                key.game.publisher.webhook_secret,
                payload,
            )

            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Expired {count} keys (queued for async delivery)."
            )
        )