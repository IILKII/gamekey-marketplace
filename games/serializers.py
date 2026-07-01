from rest_framework import serializers
from .models import Game, Publisher


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher
        exclude = ('webhook_secret',)