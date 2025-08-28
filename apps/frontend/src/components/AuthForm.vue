<script setup lang="ts">
import { ref } from "vue";
const props = defineProps<{ loading?: boolean }>();
const emit = defineEmits<{ (e:"submit", p:{username:string; password:string}):void }>();
const username = ref(""), password = ref("");
const submit = () => emit("submit", { username: username.value, password: password.value });
</script>

<template>
    <div class="flex items-center gap-2">
        <input
            v-model="username"
            placeholder="username"
            class="h-10 w-36 rounded-lg border px-3 text-sm"
        />
        <input
            v-model="password"
            type="password"
            placeholder="password"
            class="h-10 w-36 rounded-lg border px-3 text-sm"
        />
        <button
            class="px-4 h-10 rounded-lg bg-zinc-900 text-white hover:opacity-90 disabled:opacity-50"
            :disabled="props.loading || !username || !password"
            @click="submit"
        >
            {{ props.loading ? "Signing in…" : "Sign in" }}
        </button>
    </div>
</template>
