from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import ProtectedError
from .models import Developer, Game, Publisher, Genre
from .serializers import (
    DeveloperSerializer, GameSerializer,
    PublisherSerializer, GenreSerializer
)


def error_response(message, status_code):
    return Response({"error": message}, status=status_code)
# 400 bad request, якщо дані криві, наприклад, немає потрібного поля
# 404 not found, якщо об'єкта не існує
# 409 conflict, якщо ми, наприклад, намагаємось видалити розробника, у якого є ігри

# Developers views
class DeveloperListAPIView(APIView):
    def get(self, request):
        developers = Developer.objects.all()
        serializer = DeveloperSerializer(developers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeveloperSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class DeveloperDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Developer.objects.get(pk=pk)
        except Developer.DoesNotExist:
            return None

    def get(self, request, pk):
        developer = self.get_object(pk)
        if not developer:
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = DeveloperSerializer(developer)
        return Response(serializer.data)

    def put(self, request, pk):
        developer = self.get_object(pk)
        if not developer:
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = DeveloperSerializer(developer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        developer = self.get_object(pk)
        if not developer:
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)
        try:
            developer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return error_response(
                "Неможливо видалити розробника, оскільки за ним закріплені ігри.",
                status.HTTP_409_CONFLICT
            )

# Games views
class GameListAPIView(APIView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class GameDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return None

    def get(self, request, pk):
        game = self.get_object(pk)
        if not game:
            return error_response("Гру не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    def patch(self, request, pk):
        game = self.get_object(pk)
        if not game:
            return error_response("Гру не знайдено.", status.HTTP_404_NOT_FOUND)
        # partial=True patch
        serializer = GameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        game = self.get_object(pk)
        if not game:
            return error_response("Гру не знайдено.", status.HTTP_404_NOT_FOUND)
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Publisher views
class PublisherListAPIView(APIView):
    def get(self, request):
        publishers = Publisher.objects.all()
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PublisherDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            return None

    def get(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = PublisherSerializer(publisher)
        return Response(serializer.data)

    def put(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = PublisherSerializer(publisher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)
        try:
            publisher.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return error_response(
                "Неможливо видалити видавця, оскільки за ним закріплені ігри.",
                status.HTTP_409_CONFLICT
            )

# Genres views
class GenreListAPIView(APIView):
    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class GenreDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Genre.objects.get(pk=pk)
        except Genre.DoesNotExist:
            return None

    def get(self, request, pk):
        genre = self.get_object(pk)
        if not genre:
            return error_response("Жанр не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = GenreSerializer(genre)
        return Response(serializer.data)

    def put(self, request, pk):
        genre = self.get_object(pk)
        if not genre:
            return error_response("Жанр не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = GenreSerializer(genre, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        genre = self.get_object(pk)
        if not genre:
            return error_response("Жанр не знайдено.", status.HTTP_404_NOT_FOUND)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Nested games view
class DeveloperGamesAPIView(APIView):
    def get(self, request, pk):
        try:
            developer = Developer.objects.get(pk=pk)
        except Developer.DoesNotExist:
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)

        games = developer.games.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)


class PublisherGamesAPIView(APIView):
    def get(self, request, pk):
        try:
            publisher = Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)

        games = publisher.games.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)
    