<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from "vue";
import { useAuth } from "./stores/auth";
import { useChat } from "./stores/chat";
import type { Room, Message } from "./stores/chat";

const auth = useAuth();
const chat = useChat();

const username = ref("");
const password = ref("");
const activeRoomId = ref<number | null>(null);
const messageText = ref("");
const loading = ref(false);
const errorMsg = ref<string | null>(null);

const currentRoom = computed<Room | undefined>(() =>
  activeRoomId.value == null
    ? undefined
    : chat.rooms.find((r) => r.id === activeRoomId.value)
);

const currentMessages = computed<Message[]>(() =>
  activeRoomId.value ? (chat.messages[activeRoomId.value] || []) : []
);

const scroller = ref<HTMLDivElement | null>(null);
async function scrollToBottom() {
  await nextTick();
  if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight;
}
watch(currentMessages, scrollToBottom);

function initials(name: string | undefined, fallback: string) {
  if (!name) return fallback[0]?.toUpperCase() ?? "?";
  const parts = name.split(" ").filter(Boolean);
  if (parts.length === 1) return parts[0][0]?.toUpperCase() ?? "?";
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

async function doLogin() {
  errorMsg.value = null;
  try {
    loading.value = true;
    await auth.login(username.value, password.value);
    await afterLogin();
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || "Login failed";
  } finally {
    loading.value = false;
  }
}

async function afterLogin() {
  await chat.fetchRooms();
  if (chat.rooms.length) {
    activeRoomId.value = chat.rooms[0].id;
    await chat.fetchMessages(activeRoomId.value);
    scrollToBottom();
  }
}

async function selectRoom(id: number) {
  if (activeRoomId.value === id) return;
  activeRoomId.value = id;
  await chat.fetchMessages(id);
  scrollToBottom();
}

async function send() {
  const roomId = activeRoomId.value;
  const body = messageText.value.trim();
  if (!roomId || !body) return;
  try {
    await chat.sendMessage(roomId, body);
    messageText.value = "";
    scrollToBottom();
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || "Failed to send message";
  }
}

onMounted(async () => {
  try {
    await auth.fetchMe();
    await afterLogin();
  } catch {}
});
</script>

<template>
    <!-- Soft gradient background -->
    <div
        class="min-h-screen bg-gradient-to-br from-slate-100 via-zinc-100 to-slate-200 text-zinc-900"
    >
        <!-- App container (glass) -->
        <div class="mx-auto max-w-6xl px-4 py-6">
            <div
                class="backdrop-blur bg-white/70 border border-white/60 shadow-2xl rounded-2xl overflow-hidden"
            >
                <!-- Top bar -->
                <header
                    class="h-16 px-6 flex items-center justify-between border-b bg-white/60"
                >
                    <div class="flex items-center gap-2">
                        <div
                            class="h-8 w-8 rounded-lg bg-zinc-900 text-white grid place-items-center text-sm font-semibold"
                        >
                            IC
                        </div>
                        <div class="font-semibold tracking-tight">
                            Intellecta Chat
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <template v-if="auth.user">
                            <div class="flex items-center gap-2 pr-2">
                                <div
                                    class="h-8 w-8 rounded-full bg-zinc-900 text-white grid place-items-center text-xs"
                                >
                                    {{ initials(auth.user?.username, "U") }}
                                </div>
                                <span class="text-sm text-zinc-600"
                                    >Hi, <b>{{ auth.user.username }}</b></span
                                >
                            </div>
                            <button
                                class="px-3 py-1.5 rounded-lg border bg-white hover:bg-zinc-50 transition"
                                @click="auth.logout"
                            >
                                Logout
                            </button>
                        </template>
                        <template v-else>
                            <input
                                v-model="username"
                                placeholder="username"
                                class="h-10 w-40 rounded-lg border px-3 text-sm bg-white/80 focus:bg-white focus:outline-none focus:ring-2 focus:ring-zinc-300"
                            />
                            <input
                                v-model="password"
                                type="password"
                                placeholder="password"
                                class="h-10 w-40 rounded-lg border px-3 text-sm bg-white/80 focus:bg-white focus:outline-none focus:ring-2 focus:ring-zinc-300"
                            />
                            <button
                                class="px-4 h-10 rounded-lg bg-zinc-900 text-white hover:opacity-90 disabled:opacity-50 transition"
                                :disabled="loading || !username || !password"
                                @click="doLogin"
                            >
                                {{ loading ? "Signing in…" : "Sign in" }}
                            </button>
                        </template>
                    </div>
                </header>

                <!-- Inline error -->
                <div
                    v-if="errorMsg"
                    class="mx-6 mt-4 rounded-lg border border-red-200 bg-red-50 text-red-800 px-3 py-2 text-sm"
                >
                    {{ errorMsg }}
                </div>

                <!-- Body -->
                <div
                    class="grid lg:grid-cols-[300px_1fr] grid-cols-1 gap-0 mt-4 lg:mt-0"
                >
                    <!-- Sidebar -->
                    <aside class="lg:border-r">
                        <div class="px-6 py-4">
                            <div
                                class="text-[11px] font-semibold tracking-[0.08em] text-zinc-500"
                            >
                                ROOMS
                            </div>
                        </div>
                        <nav class="px-3 pb-4 space-y-1">
                            <button
                                v-for="room in chat.rooms"
                                :key="room.id"
                                @click="selectRoom(room.id)"
                                class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition"
                                :class="room.id === activeRoomId
                  ? 'bg-zinc-900 text-white shadow-sm'
                  : 'hover:bg-zinc-100 bg-white/60 border'"
                            >
                                <div
                                    class="h-7 w-7 rounded-md grid place-items-center text-xs"
                                    :class="room.id === activeRoomId ? 'bg-white/20' : 'bg-zinc-200 text-zinc-700'"
                                >
                                    #
                                </div>
                                <div class="text-sm truncate">
                                    {{ room.name || ('room ' + room.id) }}
                                </div>
                            </button>

                            <div
                                v-if="!chat.rooms.length"
                                class="px-3 py-2 text-sm text-zinc-500"
                            >
                                No rooms yet
                            </div>
                        </nav>
                    </aside>

                    <!-- Chat pane -->
                    <main class="flex flex-col min-h-[60vh]">
                        <!-- Room header -->
                        <div
                            class="px-6 py-4 border-t lg:border-t-0 lg:border-b bg-white/60"
                        >
                            <div class="font-medium">
                                {{ currentRoom?.name || 'Select a room' }}
                            </div>
                        </div>

                        <!-- Messages -->
                        <div
                            ref="scroller"
                            class="flex-1 overflow-y-auto px-4 py-6 bg-gradient-to-b from-white/70 to-white/40"
                        >
                            <template v-if="activeRoomId">
                                <div class="mx-auto max-w-2xl space-y-3">
                                    <div
                                        v-for="m in currentMessages"
                                        :key="m.id"
                                        class="flex items-end"
                                        :class="m.sender === auth.user?.id ? 'justify-end' : 'justify-start'"
                                    >
                                        <!-- Avatar (others only) -->
                                        <div
                                            v-if="m.sender !== auth.user?.id"
                                            class="h-8 w-8 rounded-full bg-zinc-300 text-zinc-700 grid place-items-center text-xs mr-2 select-none"
                                            title="Sender"
                                        >
                                            {{ 'U' }}
                                        </div>

                                        <!-- Bubble -->
                                        <div
                                            class="rounded-2xl px-4 py-2 max-w-[75%] shadow-sm ring-1"
                                            :class="m.sender === auth.user?.id
                        ? 'bg-zinc-900 text-white ring-zinc-900/10'
                        : 'bg-white text-zinc-900 ring-zinc-200'"
                                        >
                                            <div
                                                class="text-xs opacity-70 mb-0.5"
                                            >
                                                {{ new Date(m.created_at).toLocaleTimeString() }}
                                            </div>
                                            <div
                                                class="whitespace-pre-wrap leading-relaxed"
                                            >
                                                {{ m.body }}
                                            </div>
                                        </div>

                                        <!-- Spacer (self) -->
                                        <div
                                            v-if="m.sender === auth.user?.id"
                                            class="w-8 ml-2"
                                        ></div>
                                    </div>
                                </div>
                            </template>

                            <div
                                v-else
                                class="mx-auto max-w-2xl text-center text-zinc-500 py-12"
                            >
                                Pick a room from the left to start chatting.
                            </div>
                        </div>

                        <!-- Composer -->
                        <div class="border-t bg-white/70 px-4 py-4">
                            <div class="mx-auto max-w-2xl flex gap-3">
                                <input
                                    v-model="messageText"
                                    @keyup.enter="send"
                                    :disabled="!activeRoomId"
                                    placeholder="Type a message…"
                                    class="flex-1 h-12 rounded-xl border px-4 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-300 disabled:bg-zinc-100"
                                />
                                <button
                                    class="h-12 px-5 rounded-xl bg-zinc-900 text-white hover:opacity-90 disabled:opacity-40 transition"
                                    :disabled="!activeRoomId || !messageText.trim()"
                                    @click="send"
                                >
                                    Send
                                </button>
                            </div>
                        </div>
                    </main>
                </div>
            </div>
        </div>
    </div>
</template>
