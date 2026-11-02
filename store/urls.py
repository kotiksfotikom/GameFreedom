from django.urls import path
from .views import (
    DeveloperListAPIView, DeveloperDetailAPIView,
    GameListAPIView, GameDetailAPIView
)

urlpatterns = [
    path('api/developers/', DeveloperListAPIView.as_view(), name='developer-list'),
    path('api/developers/<int:pk>/', DeveloperDetailAPIView.as_view(), name='developer-detail'),

    path('api/games/', GameListAPIView.as_view(), name='game-list'),
    path('api/games/<int:pk>/', GameDetailAPIView.as_view(), name='game-detail'),
]
