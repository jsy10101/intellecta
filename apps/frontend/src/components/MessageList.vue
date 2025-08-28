<script setup lang="ts">
import { ref, nextTick, watch } from "vue";
import type { Message } from "../types/chat";
const props = defineProps<{ messages: Message[]; selfUserId: number | null }>();
const scroller = ref<HTMLDivElement|null>(null);
const scrollToBottom = async () => { await nextTick(); if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight; };
watch(() => props.messages.length, scrollToBottom);
</script>

<template>
    <div
        ref="scroller"
        class="flex-1 overflow-y-auto px-4 py-6 bg-gradient-to-b from-white/70 to-white/40"
    >
        <div class="mx-auto max-w-2xl space-y-3">
            <div
                v-for="m in props.messages"
                :key="m.id"
                class="flex items-end"
                :class="m.sender===props.selfUserId ? 'justify-end' : 'justify-start'"
            >
                <div
                    class="rounded-2xl px-4 py-2 max-w-[75%] shadow-sm ring-1"
                    :class="m.sender===props.selfUserId ? 'bg-zinc-900 text-white ring-zinc-900/10' : 'bg-white text-zinc-900 ring-zinc-200'"
                >
                    <div class="text-xs opacity-70 mb-0.5">
                        {{ new Date(m.created_at).toLocaleTimeString() }}
                    </div>
                    <div class="whitespace-pre-wrap leading-relaxed">
                        {{ m.body }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
