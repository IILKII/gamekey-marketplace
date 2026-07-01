from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from games.viewsets import GameViewSet, PublisherViewSet
from games.views import register, create_order
from games.views import register, create_order, home
router = DefaultRouter()

router.register(r'games', GameViewSet)
router.register(r'publishers', PublisherViewSet)

urlpatterns = [
    path('', home),

    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),

    path('api/register/', register),

    path('api/orders/', create_order),
]