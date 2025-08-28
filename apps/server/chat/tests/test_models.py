import pytest
from chat.models import Room, RoomMember, Message


@pytest.mark.django_db
def test_room_member_unique(user):
    r = Room.objects.create(type=Room.GROUP, name="General", created_by=user)
    RoomMember.objects.create(room=r, user=user)
    with pytest.raises(Exception):
        RoomMember.objects.create(room=r, user=user)  # unique_together


@pytest.mark.django_db
def test_message_ordering(user):
    r = Room.objects.create(type=Room.GROUP, name="G", created_by=user)
    RoomMember.objects.create(room=r, user=user)
    m1 = Message.objects.create(room=r, sender=user, body="a")
    m2 = Message.objects.create(room=r, sender=user, body="b")
    ids = list(r.messages.values_list("id", flat=True))
    assert ids == sorted(ids)  # ordering by created_at, id
    assert [m1.id, m2.id] == ids
