from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Room(models.Model):
    DM = "dm"
    GROUP = "group"
    ROOM_TYPES = [(DM, "Direct"), (GROUP, "Group")]

    type = models.CharField(max_length=10, choices=ROOM_TYPES, default=GROUP)
    name = models.CharField(max_length=255, blank=True)  # optional for DM
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="rooms_created"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()}:{self.pk}:{self.name or ''}"


class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="room_memberships"
    )
    role = models.CharField(max_length=50, default="member")
    joined_at = models.DateTimeField(default=timezone.now)
    last_read_message_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("room", "user")]
        indexes = [
            models.Index(fields=["room", "user"]),
        ]

    def __str__(self):
        return f"RoomMember(room={self.room_id}, user={self.user_id})"


class Message(models.Model):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    TYPES = [(TEXT, "Text"), (IMAGE, "Image"), (FILE, "File")]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="messages_sent"
    )
    body = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPES, default=TEXT)
    client_msg_id = models.CharField(
        max_length=64, blank=True, default=""
    )  # for idempotency (optional)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["room", "created_at"]),
        ]
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Message({self.id}) in room {self.room_id}"
