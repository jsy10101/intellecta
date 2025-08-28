from rest_framework.permissions import BasePermission
from .models import RoomMember, Room


class IsRoomMember(BasePermission):
    """
    Only allow access if request.user is a member of the target room.
    Works with views that either:
    - set self.get_room() or
    - operate on Message/Room queryset filtered by membership
    """

    def has_object_permission(self, request, view, obj):
        # obj can be Room or Message
        room_id = obj.id if isinstance(obj, Room) else getattr(obj, "room_id", None)
        if not room_id:
            return False
        return RoomMember.objects.filter(room_id=room_id, user=request.user).exists()
