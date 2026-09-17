"use client";

import { useEffect, useMemo, useState } from "react";

import { apiMessage, ticketsApi } from "@/lib/api";
import type { Ticket } from "@/lib/types";

export function useTickets(params: Record<string, string | number | undefined> = { page: 1, limit: 20 }) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const key = useMemo(() => JSON.stringify(params), [params]);

  useEffect(() => {
    let active = true;
    queueMicrotask(async () => {
      try {
        const data = await ticketsApi.list(JSON.parse(key));
        if (!active) return;
        setTickets(data.items);
        setTotal(data.total);
        setError(null);
      } catch (err) {
        if (active) setError(apiMessage(err));
      } finally {
        if (active) setLoading(false);
      }
    });
    return () => {
      active = false;
    };
  }, [key]);

  return { tickets, total, loading, error };
}
