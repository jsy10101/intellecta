import { defineStore } from "pinia";
import api from "../lib/api";

type Tokens = { access: string; refresh: string };

export const useAuth = defineStore("auth", {
    state: () => ({ user: null as null | { id: number; username: string } }),
    actions: {
        async login(username: string, password: string) {
            const { data } = await api.post<Tokens>("/api/auth/jwt/create", {
                username,
                password,
            });
            localStorage.setItem("access", data.access);
            localStorage.setItem("refresh", data.refresh);
            await this.fetchMe();
        },
        async refresh() {
            const refresh = localStorage.getItem("refresh");
            if (!refresh) return;
            const { data } = await api.post<Tokens>("/api/auth/jwt/refresh", {
                refresh,
            });
            localStorage.setItem("access", data.access);
        },
        async fetchMe() {
            const { data } = await api.get("/api/auth/users/me/");
            this.user = data;
        },
        logout() {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            this.user = null;
        },
    },
});
