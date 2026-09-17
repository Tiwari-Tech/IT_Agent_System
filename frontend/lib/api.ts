"use client";

import axios, { AxiosError } from "axios";

import type { Message, Ticket, TicketList, User } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "it_agent_token";

export const api = axios.create({ baseURL: API_BASE_URL, timeout: 15000 });

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getToken() {
  return typeof window === "undefined" ? null : localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export function apiMessage(error: unknown) {
  const err = error as AxiosError<{ detail?: string | { error?: string } }>;
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (detail?.error) return detail.error;
  return err.message || "Request failed";
}

export const authApi = {
  login: async (email: string, password: string) => (await api.post<{ access_token: string }>("/api/v1/auth/login", { email, password })).data,
  register: async (data: { email: string; password: string; name: string; role: string }) => (await api.post<User>("/api/v1/auth/register", data)).data,
  me: async () => (await api.get<User>("/api/v1/auth/me")).data,
};

export const usersApi = {
  me: async () => (await api.get<User>("/api/v1/users/me")).data,
  get: async (id: string) => (await api.get<User>(`/api/v1/users/${id}`)).data,
};

export const ticketsApi = {
  list: async (params: Record<string, string | number | undefined>) => (await api.get<TicketList>("/api/v1/tickets", { params })).data,
  get: async (id: string) => (await api.get<Ticket>(`/api/v1/tickets/${id}`)).data,
  create: async (data: { title: string; description: string; status?: string; priority?: string; category?: string }) => (await api.post<Ticket>("/api/v1/tickets", data)).data,
  update: async (id: string, data: Partial<Ticket>) => (await api.patch<Ticket>(`/api/v1/tickets/${id}`, data)).data,
  message: async (id: string, content: string) => (await api.post<Message>(`/api/v1/tickets/${id}/messages`, { content })).data,
};

export const healthApi = {
  api: async () => (await api.get("/health")).data,
  db: async () => (await api.get("/health/db")).data,
  redis: async () => (await api.get("/health/redis")).data,
};

export function createChatSocket(token: string | null) {
  const url = API_BASE_URL.replace(/^http/, "ws") + `/api/v1/ws/chat${token ? `?token=${encodeURIComponent(token)}` : ""}`;
  return new WebSocket(url);
}
