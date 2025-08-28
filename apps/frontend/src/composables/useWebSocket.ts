import { ref, onUnmounted } from "vue";

export function useWebSocket(roomId: number, token: string) {
    const wsUrl = `ws://127.0.0.1:8000/ws/chat/?token=${token}`;
    const socket = new WebSocket(wsUrl);

    const messages = ref<any[]>([]);

    socket.onopen = () => {
        socket.send(JSON.stringify({ action: "subscribe", room: roomId }));
    };

    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === "message.new") {
            messages.value.push(data.message);
        }
    };

    function send(body: string) {
        socket.send(
            JSON.stringify({ action: "send_message", room: roomId, body })
        );
    }

    onUnmounted(() => socket.close());

    return { messages, send };
}
