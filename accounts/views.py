import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .serializers import RegisterSerializer

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        tags=["Accounts"],
        summary="Реєстрація нового користувача",
        description="Створює новий обліковий запис користувача. Пароль зберігається у хешованому вигляді.",
        request=RegisterSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            logger.info("Зареєстровано нового користувача: username='%s', id=%s", user.username, user.id)
            return Response(
                {"message": "Користувача успішно зареєстровано!"},
                status=status.HTTP_201_CREATED
            )

        logger.warning(
            "Невдала спроба реєстрації (username='%s'): %s",
            request.data.get("username", "unknown"),
            serializer.errors,
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)