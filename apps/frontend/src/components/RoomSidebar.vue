<script setup lang="ts">
import type { Room } from "../types/chat";
const props = defineProps<{ rooms: Room[]; activeRoomId: number | null }>();
const emit = defineEmits<{ (e:"select", id:number):void }>();
</script>

<template>
    <aside class="lg:border-r">
        <div
            class="px-6 py-3 text-[11px] font-semibold tracking-[0.08em] text-zinc-500"
        >
            ROOMS
        </div>
        <nav class="px-3 pb-4 space-y-1">
            <button
                v-for="room in props.rooms"
                :key="room.id"
                @click="emit('select', room.id)"
                class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition"
                :class="room.id===props.activeRoomId ? 'bg-zinc-900 text-white shadow-sm' : 'hover:bg-zinc-100 bg-white/60 border'"
            >
                <div
                    class="h-7 w-7 rounded-md grid place-items-center text-xs"
                    :class="room.id===props.activeRoomId ? 'bg-white/20' : 'bg-zinc-200 text-zinc-700'"
                >
                    #
                </div>
                <div class="text-sm truncate">
                    {{ room.name || ('room ' + room.id) }}
                </div>
            </button>
            <div
                v-if="!props.rooms.length"
                class="px-3 py-2 text-sm text-zinc-500"
            >
                No rooms yet
            </div>
        </nav>
    </aside>
</template>
