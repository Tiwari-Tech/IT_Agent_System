"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { apiMessage, authApi, setToken } from "@/lib/api";
import type { User } from "@/lib/types";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; name: string; role: string }) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    authApi.me().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false));
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    loading,
    error,
    login: async (email, password) => {
      setError(null);
      try {
        const token = await authApi.login(email, password);
        setToken(token.access_token);
        setUser(await authApi.me());
      } catch (err) {
        const message = apiMessage(err);
        setError(message);
        throw new Error(message);
      }
    },
    register: async (data) => {
      setError(null);
      try {
        await authApi.register(data);
        const token = await authApi.login(data.email, data.password);
        setToken(token.access_token);
        setUser(await authApi.me());
      } catch (err) {
        const message = apiMessage(err);
        setError(message);
        throw new Error(message);
      }
    },
    logout: () => {
      setToken(null);
      setUser(null);
    },
  }), [error, loading, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
