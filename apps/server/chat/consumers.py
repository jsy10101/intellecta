from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Room

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()

    async def receive_json(self, content):
        action = content.get("action")
        if action == "subscribe":
            room_id = content["room"]
            self.room_group_name = f"room_{room_id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        elif action == "send_message":
            room_id = content["room"]
            body = content["body"]
            message = await self.save_message(room_id, body)
            await self.channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "message.new",
                    "message": {
                        "id": message.id,
                        "body": message.body,
                        "sender": message.sender_id,
                        "created_at": message.created_at.isoformat(),
                    },
                },
            )

    async def message_new(self, event):
        await self.send_json(
            {
                "type": "message.new",
                "message": event["message"],
            }
        )

    @database_sync_to_async
    def save_message(self, room_id, body):
        room = Room.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=self.scope["user"], body=body)
