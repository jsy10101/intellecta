import pytest
from chat.models import Room, RoomMember, Message


@pytest.mark.django_db
def test_create_room(auth_api, user):
    res = auth_api.post(
        "/api/rooms/", {"type": "group", "name": "General"}, format="json"
    )
    assert res.status_code == 201
    data = res.json()
    room = Room.objects.get(id=data["id"])
    assert RoomMember.objects.filter(room=room, user=user).exists()


@pytest.mark.django_db
def test_list_my_rooms(auth_api, user):
    r = Room.objects.create(type=Room.GROUP, name="General", created_by=user)
    RoomMember.objects.create(room=r, user=user)
    res = auth_api.get("/api/rooms/")
    assert res.status_code == 200
    assert len(res.json()["results"]) == 1


@pytest.mark.django_db
def test_room_messages_crud(auth_api, user):
    r = Room.objects.create(type=Room.GROUP, name="General", created_by=user)
    RoomMember.objects.create(room=r, user=user)
    # send
    res = auth_api.post(
        f"/api/rooms/{r.id}/messages/",
        {"body": "Hello", "client_msg_id": "abc-1"},
        format="json",
    )
    assert res.status_code == 201
    # list
    res = auth_api.get(f"/api/rooms/{r.id}/messages/?limit=25&offset=0")
    assert res.status_code == 200
    payload = res.json()
    assert payload["count"] == 1
    assert payload["results"][0]["body"] == "Hello"


@pytest.mark.django_db
def test_membership_enforced(api, user, user2):
    # room owned by user
    r = Room.objects.create(type=Room.GROUP, name="Private", created_by=user)
    RoomMember.objects.create(room=r, user=user)
    # authenticate as user2 (not a member)
    api.force_authenticate(user=user2)
    # cannot list private room
    res = api.get("/api/rooms/")
    assert res.status_code == 200
    assert res.json()["count"] == 0
    # cannot send message to that room
    res = api.post(f"/api/rooms/{r.id}/messages/", {"body": "x"}, format="json")
    assert res.status_code in (403, 404)  # membership blocked
