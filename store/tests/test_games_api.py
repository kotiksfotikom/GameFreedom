import pytest
from django.urls import reverse


# GET

@pytest.mark.django_db
def test_get_games_empty_list(api_client) -> None:
    response = api_client.get("/api/games/", format="json")
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_get_games_list(api_client, game) -> None:
    response = api_client.get("/api/games/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == game.title


@pytest.mark.django_db
def test_get_games_filter_search_and_sort(api_client, game, genre) -> None:
    response = api_client.get(
        f"/api/games/?search=Cyber&genre_id={genre.id}&min_price=10&max_price=100&sort_by=price&order=asc",
        format="json",
    )
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_games_invalid_filter_param(api_client) -> None:
    response = api_client.get("/api/games/?genre_id=invalid", format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_games_invalid_sort_param(api_client) -> None:
    response = api_client.get("/api/games/?sort_by=unknown_field", format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_game_detail_success(api_client, game) -> None:
    response = api_client.get(f"/api/games/{game.id}/", format="json")
    assert response.status_code == 200
    assert response.data["title"] == game.title


@pytest.mark.django_db
def test_get_game_detail_not_found(api_client) -> None:
    response = api_client.get("/api/games/9999/", format="json")
    assert response.status_code == 404


# POST

@pytest.mark.django_db
def test_create_game_no_auth(api_client, developer, publisher, genre) -> None:
    response = api_client.post(
        "/api/games/",
        {
            "title": "New Game",
            "price": "29.99",
            "release_date": "2026-05-01",
            "developer_id": developer.id,
            "publisher_id": publisher.id,
            "genre_ids": [genre.id],
        },
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_game_invalid_token(api_client, developer, publisher, genre) -> None:
    api_client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken")
    response = api_client.post(
        "/api/games/",
        {
            "title": "New Game",
            "price": "29.99",
            "release_date": "2026-05-01",
            "developer_id": developer.id,
            "publisher_id": publisher.id,
            "genre_ids": [genre.id],
        },
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_game_success(api_client, user, developer, publisher, genre) -> None:
    login_url = reverse("token_obtain_pair")
    tokens = api_client.post(
        login_url,
        {"username": "adminuser", "password": "1234"},
        format="json",
    ).data

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    response = api_client.post(
        "/api/games/",
        {
            "title": "Mystic Realms",
            "price": "39.99",
            "rating": "9.0",
            "release_date": "2026-03-15",
            "developer_id": developer.id,
            "publisher_id": publisher.id,
            "genre_ids": [genre.id],
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["title"] == "Mystic Realms"


@pytest.mark.django_db
def test_create_game_bad_request(api_client, user) -> None:
    login_url = reverse("token_obtain_pair")
    tokens = api_client.post(
        login_url,
        {"username": "adminuser", "password": "1234"},
        format="json",
    ).data

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    response = api_client.post(
        "/api/games/",
        {"title": "Incomplete Game"},
        format="json",
    )
    assert response.status_code == 400


# PATCH

@pytest.mark.django_db
def test_patch_game_no_auth(api_client, game) -> None:
    response = api_client.patch(
        f"/api/games/{game.id}/",
        {"price": "19.99"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_patch_game_success(api_client, user, game) -> None:
    login_url = reverse("token_obtain_pair")
    tokens = api_client.post(
        login_url,
        {"username": "adminuser", "password": "1234"},
        format="json",
    ).data

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    response = api_client.patch(
        f"/api/games/{game.id}/",
        {"price": "19.99"},
        format="json",
    )
    assert response.status_code == 200
    assert str(response.data["price"]) == "19.99"


@pytest.mark.django_db
def test_patch_game_not_found(api_client, user) -> None:
    login_url = reverse("token_obtain_pair")
    tokens = api_client.post(
        login_url,
        {"username": "adminuser", "password": "1234"},
        format="json",
    ).data

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    response = api_client.patch(
        "/api/games/9999/",
        {"price": "19.99"},
        format="json",
    )
    assert response.status_code == 404


# DELETE

@pytest.mark.django_db
def test_delete_game_no_auth(api_client, game) -> None:
    response = api_client.delete(f"/api/games/{game.id}/", format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_game_success(api_client, user, game) -> None:
    login_url = reverse("token_obtain_pair")
    tokens = api_client.post(
        login_url,
        {"username": "adminuser", "password": "1234"},
        format="json",
    ).data

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    response = api_client.delete(f"/api/games/{game.id}/", format="json")
    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_game_not_found(api_client, user) -> None:
    login_url = reverse("token_obtain_pair")
    tokens = api_client.post(
        login_url,
        {"username": "adminuser", "password": "1234"},
        format="json",
    ).data

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    response = api_client.delete("/api/games/9999/", format="json")
    assert response.status_code == 404
