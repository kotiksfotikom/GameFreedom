from rest_framework import serializers
from .models import Developer, Publisher, Genre, Game


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
    developer = DeveloperSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    developer_id = serializers.PrimaryKeyRelatedField(
        queryset=Developer.objects.all(), source='developer', write_only=True
    )
    publisher_id = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), source='publisher', write_only=True
    )
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), source='genres', write_only=True, many=True
    )

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'description', 'price', 'rating', 'release_date',
            'cover_image_url', 'min_system_requirements', 'rec_system_requirements',
            'developer', 'publisher', 'genres',
            'developer_id', 'publisher_id', 'genre_ids'
        ]
