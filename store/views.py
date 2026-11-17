import logging
from decimal import Decimal, InvalidOperation

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import ProtectedError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from .models import Developer, Game, Publisher, Genre
from .serializers import (
    DeveloperSerializer, GameSerializer,
    PublisherSerializer, GenreSerializer
)

logger = logging.getLogger(__name__)


def error_response(message, status_code):
    return Response({"error": message}, status=status_code)


# Developers views
class DeveloperListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DeveloperSerializer

    @extend_schema(tags=["Developers"], summary="Отримати список розробників", responses={200: DeveloperSerializer(many=True)})
    def get(self, request):
        developers = Developer.objects.all()
        serializer = DeveloperSerializer(developers, many=True)
        return Response(serializer.data)

    @extend_schema(tags=["Developers"], summary="Створити розробника", request=DeveloperSerializer, responses={201: DeveloperSerializer, 400: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT})
    def post(self, request):
        serializer = DeveloperSerializer(data=request.data)
        if serializer.is_valid():
            dev = serializer.save()
            logger.info("Користувач '%s' створив розробника id=%s (%s)", request.user.username, dev.id, dev.name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning("Помилка валідації при створенні розробника користувачем '%s': %s", request.user.username, serializer.errors)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class DeveloperDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DeveloperSerializer

    def get_object(self, pk):
        try:
            return Developer.objects.get(pk=pk)
        except Developer.DoesNotExist:
            return None

    @extend_schema(tags=["Developers"], summary="Деталі розробника", responses={200: DeveloperSerializer, 404: OpenApiTypes.OBJECT})
    def get(self, request, pk):
        developer = self.get_object(pk)
        if not developer:
            logger.warning("Запит неіснуючого розробника id=%s", pk)
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = DeveloperSerializer(developer)
        return Response(serializer.data)

    @extend_schema(tags=["Developers"], summary="Оновити розробника", request=DeveloperSerializer, responses={200: DeveloperSerializer, 400: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT})
    def put(self, request, pk):
        developer = self.get_object(pk)
        if not developer:
            logger.warning("Спроба оновити неіснуючого розробника id=%s", pk)
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = DeveloperSerializer(developer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Користувач '%s' оновив розробника id=%s", request.user.username, pk)
            return Response(serializer.data)
        logger.warning("Помилка валідації при оновленні розробника id=%s: %s", pk, serializer.errors)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=["Developers"], summary="Видалити розробника", responses={204: None, 401: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT, 409: OpenApiTypes.OBJECT})
    def delete(self, request, pk):
        developer = self.get_object(pk)
        if not developer:
            logger.warning("Спроба видалити неіснуючого розробника id=%s", pk)
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)
        try:
            developer.delete()
            logger.info("Користувач '%s' видалив розробника id=%s", request.user.username, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            logger.warning("Конфлікт при видаленні розробника id=%s: закріплені ігри", pk)
            return error_response(
                "Неможливо видалити розробника, оскільки за ним закріплені ігри.",
                status.HTTP_409_CONFLICT
            )


# Games views
class GameListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = GameSerializer
    SORT_FIELDS = {'price', 'rating', 'release_date'}

    @extend_schema(
        tags=["Games"],
        summary="Отримати список ігор",
        description="Повертає список усіх відеоігор з підтримкою пошуку, фільтрації за жанром/розробником/видавцем/ціною та сортування. Доступно всім користувачам без автентифікації.",
        parameters=[
            OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Пошук за назвою гри (без урахування регістру)"),
            OpenApiParameter(name="genre_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Фільтр за ID жанру"),
            OpenApiParameter(name="developer_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Фільтр за ID розробника"),
            OpenApiParameter(name="publisher_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Фільтр за ID видавця"),
            OpenApiParameter(name="min_price", type=OpenApiTypes.DECIMAL, location=OpenApiParameter.QUERY, description="Мінімальна ціна гри"),
            OpenApiParameter(name="max_price", type=OpenApiTypes.DECIMAL, location=OpenApiParameter.QUERY, description="Максимальна ціна гри"),
            OpenApiParameter(name="sort_by", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Поле для сортування", enum=["price", "rating", "release_date"]),
            OpenApiParameter(name="order", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Напрямок сортування (за замовчуванням asc)", enum=["asc", "desc"]),
        ],
        responses={
            200: GameSerializer(many=True),
            400: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request):
        params = request.query_params
        logger.debug("Запит списку ігор з параметрами: %s", dict(params))
        games = Game.objects.select_related('developer', 'publisher').prefetch_related('genres')

        # пошук за назвою
        search = params.get('search')
        if search:
            games = games.filter(title__icontains=search)

        # фільтри за id жанру, розробника, видавця
        id_filters = (
            ('genre_id', 'genres__id'),
            ('developer_id', 'developer_id'),
            ('publisher_id', 'publisher_id'),
        )
        for param, field in id_filters:
            value = params.get(param)
            if value:
                try:
                    games = games.filter(**{field: int(value)})
                except ValueError:
                    logger.warning("Некоректний числовий параметр фільтрації '%s=%s'", param, value)
                    return error_response(f"Параметр {param} має бути числом.", status.HTTP_400_BAD_REQUEST)

        # діапазон ціни
        for param, lookup in (('min_price', 'price__gte'), ('max_price', 'price__lte')):
            value = params.get(param)
            if value:
                try:
                    games = games.filter(**{lookup: Decimal(value)})
                except InvalidOperation:
                    logger.warning("Некоректний параметр ціни '%s=%s'", param, value)
                    return error_response(f"Параметр {param} має бути числом.", status.HTTP_400_BAD_REQUEST)

        # сортування
        sort_by = params.get('sort_by')
        order = params.get('order', 'asc')
        if order not in ('asc', 'desc'):
            logger.warning("Некоректний параметр order='%s'", order)
            return error_response("Параметр order має бути asc або desc.", status.HTTP_400_BAD_REQUEST)
        if sort_by:
            if sort_by not in self.SORT_FIELDS:
                logger.warning("Некоректний параметр sort_by='%s'", sort_by)
                return error_response(
                    "Параметр sort_by має бути price, rating або release_date.",
                    status.HTTP_400_BAD_REQUEST
                )
            games = games.order_by(f"-{sort_by}" if order == 'desc' else sort_by)

        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Games"],
        summary="Створити нову гру",
        description="Додає нову відеогру до каталогу. Потрібна JWT-автентифікація (`Authorization: Bearer <token>`).",
        request=GameSerializer,
        examples=[
            OpenApiExample(
                "Приклад створення гри",
                value={
                    "title": "Cyber Odyssey 2088",
                    "description": "Кіберпанкова рольова гра",
                    "price": "59.99",
                    "rating": "9.2",
                    "release_date": "2026-05-20",
                    "developer_id": 1,
                    "publisher_id": 1,
                    "genre_ids": [1],
                },
                request_only=True,
            )
        ],
        responses={
            201: GameSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            game = serializer.save()
            logger.info("Користувач '%s' створив нову гру id=%s ('%s')", request.user.username, game.id, game.title)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning("Помилка валідації при створенні гри користувачем '%s': %s", request.user.username, serializer.errors)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class GameDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = GameSerializer

    def get_object(self, pk):
        try:
            return Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return None

    @extend_schema(
        tags=["Games"],
        summary="Отримати деталі гри",
        description="Повертає повну інформацію про гру за її ID. Доступно всім користувачам.",
        responses={
            200: GameSerializer,
            404: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request, pk):
        game = self.get_object(pk)
        if not game:
            logger.warning("Запит неіснуючої гри id=%s", pk)
            return error_response("Гру не знайдено.", status.HTTP_404_NOT_FOUND)
        logger.debug("Перегляд деталей гри id=%s ('%s')", game.id, game.title)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    @extend_schema(
        tags=["Games"],
        summary="Частково оновити гру",
        description="Оновлює вказані поля гри за її ID. Потрібна JWT-автентифікація.",
        request=GameSerializer,
        responses={
            200: GameSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def patch(self, request, pk):
        game = self.get_object(pk)
        if not game:
            logger.warning("Спроба оновити неіснуючу гру id=%s користувачем '%s'", pk, request.user.username)
            return error_response("Гру не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = GameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Користувач '%s' оновив гру id=%s", request.user.username, pk)
            return Response(serializer.data)
        logger.warning("Помилка валідації при оновленні гри id=%s: %s", pk, serializer.errors)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Games"],
        summary="Видалити гру",
        description="Видаляє гру з каталогу за її ID. Потрібна JWT-автентифікація.",
        responses={
            204: None,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def delete(self, request, pk):
        game = self.get_object(pk)
        if not game:
            logger.warning("Спроба видалити неіснуючу гру id=%s користувачем '%s'", pk, request.user.username)
            return error_response("Гру не знайдено.", status.HTTP_404_NOT_FOUND)
        game.delete()
        logger.info("Користувач '%s' видалив гру id=%s", request.user.username, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


# Publisher views
class PublisherListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PublisherSerializer

    @extend_schema(tags=["Publishers"], summary="Отримати список видавців", responses={200: PublisherSerializer(many=True)})
    def get(self, request):
        publishers = Publisher.objects.all()
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data)

    @extend_schema(tags=["Publishers"], summary="Створити видавця", request=PublisherSerializer, responses={201: PublisherSerializer, 400: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT})
    def post(self, request):
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            pub = serializer.save()
            logger.info("Користувач '%s' створив видавця id=%s (%s)", request.user.username, pub.id, pub.name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PublisherDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PublisherSerializer

    def get_object(self, pk):
        try:
            return Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            return None

    @extend_schema(tags=["Publishers"], summary="Деталі видавця", responses={200: PublisherSerializer, 404: OpenApiTypes.OBJECT})
    def get(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = PublisherSerializer(publisher)
        return Response(serializer.data)

    @extend_schema(tags=["Publishers"], summary="Оновити видавця", request=PublisherSerializer, responses={200: PublisherSerializer, 400: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT})
    def put(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = PublisherSerializer(publisher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Користувач '%s' оновив видавця id=%s", request.user.username, pk)
            return Response(serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=["Publishers"], summary="Видалити видавця", responses={204: None, 401: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT, 409: OpenApiTypes.OBJECT})
    def delete(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)
        try:
            publisher.delete()
            logger.info("Користувач '%s' видалив видавця id=%s", request.user.username, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            logger.warning("Конфлікт при видаленні видавця id=%s: закріплені ігри", pk)
            return error_response(
                "Неможливо видалити видавця, оскільки за ним закріплені ігри.",
                status.HTTP_409_CONFLICT
            )


# Genres views
class GenreListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = GenreSerializer

    @extend_schema(tags=["Genres"], summary="Отримати список жанрів", responses={200: GenreSerializer(many=True)})
    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    @extend_schema(tags=["Genres"], summary="Створити жанр", request=GenreSerializer, responses={201: GenreSerializer, 400: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT})
    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            genre = serializer.save()
            logger.info("Користувач '%s' створив жанр id=%s (%s)", request.user.username, genre.id, genre.name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class GenreDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = GenreSerializer

    def get_object(self, pk):
        try:
            return Genre.objects.get(pk=pk)
        except Genre.DoesNotExist:
            return None

    @extend_schema(tags=["Genres"], summary="Деталі жанру", responses={200: GenreSerializer, 404: OpenApiTypes.OBJECT})
    def get(self, request, pk):
        genre = self.get_object(pk)
        if not genre:
            return error_response("Жанр не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = GenreSerializer(genre)
        return Response(serializer.data)

    @extend_schema(tags=["Genres"], summary="Оновити жанр", request=GenreSerializer, responses={200: GenreSerializer, 400: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT})
    def put(self, request, pk):
        genre = self.get_object(pk)
        if not genre:
            return error_response("Жанр не знайдено.", status.HTTP_404_NOT_FOUND)
        serializer = GenreSerializer(genre, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Користувач '%s' оновив жанр id=%s", request.user.username, pk)
            return Response(serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=["Genres"], summary="Видалити жанр", responses={204: None, 401: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT})
    def delete(self, request, pk):
        genre = self.get_object(pk)
        if not genre:
            return error_response("Жанр не знайдено.", status.HTTP_404_NOT_FOUND)
        genre.delete()
        logger.info("Користувач '%s' видалив жанр id=%s", request.user.username, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


# Nested games view
class DeveloperGamesAPIView(APIView):
    serializer_class = GameSerializer

    @extend_schema(tags=["Developers"], summary="Отримати всі ігри розробника", responses={200: GameSerializer(many=True), 404: OpenApiTypes.OBJECT})
    def get(self, request, pk):
        try:
            developer = Developer.objects.get(pk=pk)
        except Developer.DoesNotExist:
            return error_response("Розробника не знайдено.", status.HTTP_404_NOT_FOUND)

        games = developer.games.select_related('developer', 'publisher').prefetch_related('genres')
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)


class PublisherGamesAPIView(APIView):
    serializer_class = GameSerializer

    @extend_schema(tags=["Publishers"], summary="Отримати всі ігри видавця", responses={200: GameSerializer(many=True), 404: OpenApiTypes.OBJECT})
    def get(self, request, pk):
        try:
            publisher = Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            return error_response("Видавця не знайдено.", status.HTTP_404_NOT_FOUND)

        games = publisher.games.select_related('developer', 'publisher').prefetch_related('genres')
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)
