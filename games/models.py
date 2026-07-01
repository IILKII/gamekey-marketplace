from django.db import models
from django.contrib.auth.models import User


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    webhook_url = models.URLField()
    webhook_secret = models.CharField(max_length=64)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Game(models.Model):
    title = models.CharField(max_length=200)

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    def __str__(self):
        return self.title


class GameKey(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired')
    ]

    key_string = models.CharField(
        max_length=50,
        unique=True
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )

    expires_at = models.DateTimeField()

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.key_string
    
class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    purchased_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    game_key = models.OneToOneField(
        GameKey,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"OrderItem {self.id}"
    
class WebhookDeliveryLog(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE
    )

    game_key = models.ForeignKey(
        GameKey,
        on_delete=models.CASCADE
    )

    event = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    response_code = models.IntegerField(
        null=True,
        blank=True
    )

    response_body = models.TextField(
        blank=True
    )

    attempts = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.event} ({self.status})"