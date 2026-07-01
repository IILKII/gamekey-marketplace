from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import AllowAny

from rest_framework.response import Response

from rest_framework import status

import uuid

from datetime import timedelta

from django.db import transaction

from django.utils import timezone

from .models import Game, GameKey, Order, OrderItem

from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([AllowAny])

def register(request):

    username = request.data.get('username')

    password = request.data.get('password')

    if not username or not password:

        return Response(
            {'error': 'Username and password required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        password=password
    )

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {'token': token.key},
        status=status.HTTP_201_CREATED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])

def create_order(request):

    game_id = request.data.get('game_id')

    if not game_id:
        return Response(
            {'error': 'game_id is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        game = Game.objects.get(id=game_id)

    except Game.DoesNotExist:

        return Response(
            {'error': 'Game not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    with transaction.atomic():

        existing_key = (
            GameKey.objects.select_for_update()
            .filter(
                game=game,
                status='active',
                owner__isnull=True
            )
            .first()
        )

        if existing_key:

            key = existing_key

            key.owner = request.user

            key.save()

        else:

            key = GameKey.objects.create(

                key_string=str(uuid.uuid4()).upper(),

                game=game,

                status='active',

                expires_at=timezone.now() + timedelta(days=30),

                owner=request.user,
            )

        order = Order.objects.create(
            user=request.user
        )

        OrderItem.objects.create(
            order=order,
            game_key=key
        )

    return Response(
        {
            'order_id': order.id,
            'game': game.title,
            'key': key.key_string,
            'expires_at': key.expires_at,
        },
        status=status.HTTP_201_CREATED
    )

from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <h1>🎮 Game Key Marketplace API</h1>
    <p>Backend is running successfully.</p>

    <h2>Available Endpoints</h2>

    <ul>
        <li>/admin/</li>
        <li>/api/games/</li>
        <li>/api/publishers/</li>
        <li>/api/register/</li>
        <li>/api/orders/</li>
    </ul>

    <p>Created using Django REST Framework.</p>
    """)