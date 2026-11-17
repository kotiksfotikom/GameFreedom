from django.urls import path
from .views import (
    DeveloperListAPIView, DeveloperDetailAPIView, DeveloperGamesAPIView,
    PublisherListAPIView, PublisherDetailAPIView, PublisherGamesAPIView,
    GenreListAPIView, GenreDetailAPIView,
    GameListAPIView, GameDetailAPIView
)

urlpatterns = [
    # Розробники
    path('api/developers/', DeveloperListAPIView.as_view()),
    path('api/developers/<int:pk>/', DeveloperDetailAPIView.as_view()),
    path('api/developers/<int:pk>/games/', DeveloperGamesAPIView.as_view()),

    # Видавці
    path('api/publishers/', PublisherListAPIView.as_view()),
    path('api/publishers/<int:pk>/', PublisherDetailAPIView.as_view()),
    path('api/publishers/<int:pk>/games/', PublisherGamesAPIView.as_view()),

    # Жанри
    path('api/genres/', GenreListAPIView.as_view()),
    path('api/genres/<int:pk>/', GenreDetailAPIView.as_view()),

    # Ігри
    path('api/games/', GameListAPIView.as_view()),
    path('api/games/<int:pk>/', GameDetailAPIView.as_view()),
]
