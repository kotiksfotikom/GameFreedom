from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import ProtectedError
from .models import Developer, Game
from .serializers import DeveloperSerializer, GameSerializer


def error_response(message, status_code):
    return Response({"error": message}, status=status_code)

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
