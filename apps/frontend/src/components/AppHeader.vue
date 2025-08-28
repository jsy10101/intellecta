<script setup lang="ts">
defineProps<{ user: { id:number; username:string } | null }>();
const emit = defineEmits<{ (e:"logout"):void }>();
</script>

<template>
    <header
        class="h-16 px-6 flex items-center justify-between border-b bg-white/60"
    >
        <div class="flex items-center gap-2">
            <div
                class="h-8 w-8 rounded-lg bg-zinc-900 text-white grid place-items-center text-sm font-semibold"
            >
                IC
            </div>
            <div class="font-semibold tracking-tight">Intellecta Chat</div>
        </div>
        <div class="flex items-center gap-3">
            <template v-if="user">
                <span class="text-sm text-zinc-600"
                    >Hi, <b>{{ user.username }}</b></span
                >
                <button
                    class="px-3 py-1.5 rounded-lg border bg-white hover:bg-zinc-50"
                    @click="emit('logout')"
                >
                    Logout
                </button>
            </template>
            <slot v-else />
            <!-- place AuthForm here -->
        </div>
    </header>
</template>
