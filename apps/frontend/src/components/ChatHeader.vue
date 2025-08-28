<script setup lang="ts">
import type { Room } from "../types/chat";
defineProps<{ room?: Room }>();
</script>
<template>
    <div class="px-6 py-4 border-b bg-white/60">
        <div class="font-medium">{{ room?.name || 'Select a room' }}</div>
    </div>
</template>
