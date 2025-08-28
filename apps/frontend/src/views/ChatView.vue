<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useAuth } from "../stores/auth";
import { useChat } from "../stores/chat";
import { useWebSocket } from "../composables/useWebSocket";
import AppHeader from "../components/AppHeader.vue";
import AuthForm from "../components/AuthForm.vue";
import RoomSidebar from "../components/RoomSidebar.vue";
import ChatHeader from "../components/ChatHeader.vue";
import MessageList from "../components/MessageList.vue";
import MessageComposer from "../components/MessageComposer.vue";
import type { Room, Message } from "../types/chat";

const auth = useAuth();
const chat = useChat();

const activeRoomId = ref<number | null>(null);
const loading = ref(false);
const errorMsg = ref<string | null>(null);

const currentRoom = computed<Room | undefined>(() =>
  activeRoomId.value == null ? undefined : chat.rooms.find(r => r.id === activeRoomId.value)
);
const currentMessages = computed<Message[]>(() =>
  activeRoomId.value ? (chat.messages[activeRoomId.value] || []) : []
);

// --- WS glue ---
let ws: ReturnType<typeof useWebSocket> | null = null;
const accessToken = computed(() => localStorage.getItem("access") || "");

// Reconnect WS whenever room or token changes
watch([activeRoomId, accessToken], ([roomId, token], _old, onCleanup) => {
  // close previous socket
  if (ws && (ws as any).close) (ws as any).close();
  ws = null;

  if (!roomId || !token) return;

  // open new socket and subscribe to room
  ws = useWebSocket(roomId, token);

  // pipe incoming WS messages into Pinia store (dedupe by id)
  const stop = watch(ws.messages, (list) => {
    if (!roomId) return;
    const last = list[list.length - 1];
    if (!last) return;
    const arr = chat.messages[roomId] || [];
    if (!arr.some(m => m.id === last.id)) {
      chat.messages[roomId] = [...arr, last];
    }
  });

  onCleanup(() => {
    stop();
    if (ws && (ws as any).close) (ws as any).close();
  });
});

// ---------

async function login(p: { username:string; password:string }) {
  errorMsg.value = null; loading.value = true;
  try { await auth.login(p.username, p.password); await afterLogin(); }
  catch (e:any) { errorMsg.value = e?.response?.data?.detail || "Login failed"; }
  finally { loading.value = false; }
}

async function afterLogin() {
  await chat.fetchRooms();
  if (chat.rooms.length) {
    activeRoomId.value = chat.rooms[0].id;
    await chat.fetchMessages(activeRoomId.value);
  }
}

async function selectRoom(id:number) {
  if (activeRoomId.value===id) return;
  activeRoomId.value = id;
  await chat.fetchMessages(id); // initial history via REST; live updates via WS
}

// We keep sending via REST; WS will broadcast the saved message back.
// (If your consumer supports sending over WS, we can switch later.)
async function send(body:string) {
  if (!activeRoomId.value) return;
  await chat.sendMessage(activeRoomId.value, body);
}

onMounted(async () => {
  try { await auth.fetchMe(); await afterLogin(); } catch {}
});
</script>

<template>
    <div
        class="min-h-screen bg-gradient-to-br from-slate-100 via-zinc-100 to-slate-200 text-zinc-900"
    >
        <div class="mx-auto max-w-6xl px-4 py-6">
            <div
                class="backdrop-blur bg-white/70 border border-white/60 shadow-2xl rounded-2xl overflow-hidden"
            >
                <AppHeader :user="auth.user" @logout="auth.logout">
                    <AuthForm
                        v-if="!auth.user"
                        :loading="loading"
                        @submit="login"
                    />
                </AppHeader>

                <div
                    v-if="errorMsg"
                    class="mx-6 mt-4 rounded-lg border border-red-200 bg-red-50 text-red-800 px-3 py-2 text-sm"
                >
                    {{ errorMsg }}
                </div>

                <div class="grid lg:grid-cols-[300px_1fr] grid-cols-1">
                    <RoomSidebar
                        :rooms="chat.rooms"
                        :activeRoomId="activeRoomId"
                        @select="selectRoom"
                    />
                    <section class="flex flex-col min-h-[60vh]">
                        <ChatHeader :room="currentRoom" />
                        <MessageList
                            :messages="currentMessages"
                            :selfUserId="auth.user?.id ?? null"
                        />
                        <MessageComposer
                            :disabled="!activeRoomId"
                            @send="send"
                        />
                    </section>
                </div>
            </div>
        </div>
    </div>
</template>
