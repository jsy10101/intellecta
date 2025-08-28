import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="alice", password="AlicePass123", email="a@example.com"
    )


@pytest.fixture
def user2(db):
    return User.objects.create_user(
        username="bob", password="BobPass123", email="b@example.com"
    )


@pytest.fixture
def auth_api(api, user):
    api.force_authenticate(user=user)
    return api
