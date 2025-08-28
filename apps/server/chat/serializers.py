from django.db import transaction
from rest_framework import serializers
from .models import Room, RoomMember, Message


class RoomMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMember
        fields = ["user", "role", "joined_at", "last_read_message_id"]


class RoomSerializer(serializers.ModelSerializer):
    members = RoomMemberSerializer(many=True, read_only=True)
    last_message_at = serializers.DateTimeField(
        source="messages.last.created_at", read_only=True
    )

    class Meta:
        model = Room
        fields = [
            "id",
            "type",
            "name",
            "created_by",
            "created_at",
            "members",
            "last_message_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "members",
            "last_message_at",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        with transaction.atomic():
            room = Room.objects.create(created_by=user, **validated_data)
            RoomMember.objects.create(room=room, user=user, role="owner")
        return room


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "body", "type", "client_msg_id", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        room = attrs.get("room")
        if not RoomMember.objects.filter(room=room, user=user).exists():
            raise serializers.ValidationError("You are not a member of this room.")
        # Idempotency: if client sends the same client_msg_id again, return existing
        cmid = attrs.get("client_msg_id")
        if cmid:
            existing = Message.objects.filter(
                room=room, sender=user, client_msg_id=cmid
            ).first()
            if existing:
                # attach for create() to short-circuit
                self.context["existing_message"] = existing
        return attrs

    def create(self, validated_data):
        existing = self.context.get("existing_message")
        if existing:
            return existing
        return Message.objects.create(**validated_data)
