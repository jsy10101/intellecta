from django.db.models import Exists, OuterRef
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Room, RoomMember, Message
from .serializers import RoomSerializer, MessageSerializer
from .permissions import IsRoomMember


class RoomViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Room.objects.annotate(
                is_member=Exists(
                    RoomMember.objects.filter(room=OuterRef("pk"), user=user)
                )
            )
            .filter(is_member=True)
            .order_by("-created_at")
            .prefetch_related("members")
        )

    def perform_create(self, serializer):
        serializer.save()  # create() sets created_by + owner membership

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        # Ensure membership
        room = self.get_object()  # leverages get_queryset -> membership enforced
        if request.method.lower() == "get":
            qs = Message.objects.filter(room=room).order_by("-created_at", "-id")
            page = self.paginate_queryset(qs)
            ser = MessageSerializer(page, many=True)
            return self.get_paginated_response(ser.data)
        # POST -> send message
        data = request.data.copy()
        data["room"] = room.id
        ser = MessageSerializer(data=data, context={"request": request})
        ser.is_valid(raise_exception=True)
        msg = ser.save()
        return Response(MessageSerializer(msg).data, status=201)


class MessageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Optional generic messages list: /api/messages?room=<id>
    Handy for search/global views. Membership enforced by filtering.
    """

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        room_id = self.request.query_params.get("room")
        qs = Message.objects.filter(room__members__user=user).select_related(
            "room", "sender"
        )
        if room_id:
            qs = qs.filter(room_id=room_id)
        return qs.order_by("-created_at", "-id")
