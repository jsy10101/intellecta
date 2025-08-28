import { defineStore } from "pinia";
import api from "../lib/api";

export interface Room {
    id: number;
    name: string;
    type: "dm" | "group";
}
export interface Message {
    id: number;
    room: number;
    body: string;
    created_at: string;
    sender: number;
}

export const useChat = defineStore("chat", {
    state: () => ({
        rooms: [] as Room[],
        messages: {} as Record<number, Message[]>, // roomId -> messages
    }),
    actions: {
        async fetchRooms() {
            const { data } = await api.get("/api/rooms/");
            this.rooms = data.results ?? data; // handles paginated/non-paginated
        },
        async fetchMessages(roomId: number, limit = 25, offset = 0) {
            const { data } = await api.get(
                `/api/rooms/${roomId}/messages/?limit=${limit}&offset=${offset}`
            );
            this.messages[roomId] = data.results ?? data;
        },
        async sendMessage(roomId: number, body: string) {
            const { data } = await api.post(`/api/rooms/${roomId}/messages/`, {
                body,
                client_msg_id: crypto.randomUUID(),
            });
            this.messages[roomId] = [data, ...(this.messages[roomId] || [])];
        },
    },
});
