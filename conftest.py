import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from store.models import Developer, Publisher, Genre, Game


@pytest.fixture(scope="function")
def api_client() -> APIClient:
    """
    Fixture to provide an API client
    """
    return APIClient()


@pytest.fixture(scope="function")
def user() -> User:
    return User.objects.create_user(
        username='adminuser',
        password='1234',
        email='adminuser@gmail.com',
    )


@pytest.fixture(scope="function")
def developer() -> Developer:
    return Developer.objects.create(
        name='Neon Interactive',
        country='Ukraine',
        description='Indie studio',
    )


@pytest.fixture(scope="function")
def publisher() -> Publisher:
    return Publisher.objects.create(
        name='Global Games',
    )


@pytest.fixture(scope="function")
def genre() -> Genre:
    return Genre.objects.create(
        name='RPG',
    )


@pytest.fixture(scope="function")
def game(developer, publisher, genre) -> Game:
    created_game = Game.objects.create(
        title='Cyber Odyssey 2088',
        description='Cyberpunk RPG',
        price='59.99',
        rating='4.8',
        release_date='2025-11-20',
        developer=developer,
        publisher=publisher,
    )
    created_game.genres.add(genre)
    return created_game
