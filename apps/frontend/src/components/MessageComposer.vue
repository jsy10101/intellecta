<script setup lang="ts">
import { ref, computed } from "vue";

const props = defineProps<{ disabled?: boolean }>();
const emit = defineEmits<{ (e: "send", body: string): void }>();

const text = ref("");

const canSend = computed(() => {
  const body = text.value.trim();
  return !props.disabled && body.length > 0;
});

function submit() {
  const body = text.value.trim();
  if (!canSend.value) return;
  emit("send", body);
  text.value = "";
}
</script>

<template>
    <div class="border-t bg-white/70 px-4 py-4">
        <div class="mx-auto max-w-2xl flex gap-3">
            <input
                v-model="text"
                @keyup.enter="submit"
                :disabled="props.disabled"
                placeholder="Type a message…"
                class="flex-1 h-12 rounded-xl border px-4 bg-white
               focus:outline-none focus:ring-2 focus:ring-zinc-300 disabled:bg-zinc-100"
            />
            <button
                class="h-12 px-5 rounded-xl bg-zinc-900 text-white hover:opacity-90 disabled:opacity-40"
                :disabled="!canSend"
                @click="submit"
            >
                Send
            </button>
        </div>
    </div>
</template>
