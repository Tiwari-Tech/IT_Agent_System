"use client";

import axios, { AxiosError } from "axios";

import type { DocumentItem, Message, Ticket, TicketList, User, WorkflowResult } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";
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
  const err = error as AxiosError<{ detail?: string | { error?: string }; error?: { message?: string } }>;
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (detail?.error) return detail.error;
  if (err.response?.data?.error?.message) return err.response.data.error.message;
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
  ollama: async () => (await api.get("/health/ollama")).data,
};

export const workflowsApi = {
  runTicket: async (ticketId: string) => (await api.post<WorkflowResult>(`/api/v1/workflows/tickets/${ticketId}/run`)).data,
};

export const documentsApi = {
  list: async () => (await api.get<{ items: DocumentItem[] }>("/api/v1/documents")).data,
  get: async (id: string) => (await api.get<DocumentItem>(`/api/v1/documents/${id}`)).data,
  upload: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return (await api.post<DocumentItem>("/api/v1/documents/upload", form)).data;
  },
  ingest: async (id: string) => (await api.post<{ document_id: string; chunks: number }>(`/api/v1/documents/${id}/ingest`)).data,
  ingestTask: async (id: string) => (await api.post<{ task_id: string; status: string }>(`/api/v1/documents/${id}/ingest-task`)).data,
};

export const jiraApi = {
  createIssue: async (data: { summary: string; description: string; issue_type?: string }) => (await api.post<{ data: Record<string, unknown> }>("/api/v1/jira/issues", data)).data,
  getIssue: async (key: string) => (await api.get<{ data: Record<string, unknown> }>(`/api/v1/jira/issues/${key}`)).data,
  updateIssue: async (key: string, fields: Record<string, unknown>) => (await api.patch<{ data: Record<string, unknown> }>(`/api/v1/jira/issues/${key}`, { fields })).data,
  addComment: async (key: string, body: string) => (await api.post<{ data: Record<string, unknown> }>(`/api/v1/jira/issues/${key}/comments`, { body })).data,
  syncStatus: async (ticketId: string, transition_id: string) => (await api.post<{ ok: boolean }>(`/api/v1/jira/tickets/${ticketId}/sync-status`, { transition_id })).data,
};

export function createChatSocket(token: string | null) {
  const base = API_BASE_URL
    ? API_BASE_URL.replace(/^http/, "ws")
    : `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`;
  const url = `${base}/api/v1/ws/chat${token ? `?token=${encodeURIComponent(token)}` : ""}`;
  return new WebSocket(url);
}
