"use client";

import { Activity, Bot, Database, GitBranch, Server, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/states";
import { apiMessage, healthApi } from "@/lib/api";

type Health = Record<string, { ok: boolean; detail: string }>;

export default function MonitoringPage() {
  const [health, setHealth] = useState<Health>({});
  useEffect(() => {
    for (const [key, fn] of Object.entries(healthApi)) {
      fn().then(() => setHealth((prev) => ({ ...prev, [key]: { ok: true, detail: "healthy" } }))).catch((err) => setHealth((prev) => ({ ...prev, [key]: { ok: false, detail: apiMessage(err) } })));
    }
  }, []);
  return (
    <AppShell>
      <div className="space-y-4">
        <div><h1 className="text-2xl font-semibold">Monitoring</h1><p className="text-sm text-slate-500">Live checks use current health endpoints; future systems show unavailable states.</p></div>
      <div className="grid gap-4 md:grid-cols-3">
        <HealthCard icon={Server} title="API" state={health.api} />
        <HealthCard icon={Database} title="PostgreSQL" state={health.db} />
        <HealthCard icon={Activity} title="Redis/Valkey" state={health.redis} />
        <Card title="Ollama"><Bot className="mb-3 text-slate-400" /><EmptyState title="Health endpoint not wired" detail="Frontend is ready for Ollama status once backend exposes it." /></Card>
        <Card title="Jira"><GitBranch className="mb-3 text-slate-400" /><EmptyState title="Health endpoint pending" detail="No Jira health API exists yet." /></Card>
        <Card title="Recent failures"><ShieldAlert className="mb-3 text-slate-400" /><EmptyState title="No failure API yet" detail="Agent and integration failures will appear here when backend tracking exists." /></Card>
      </div>
      </div>
    </AppShell>
  );
}

function HealthCard({ icon: Icon, title, state }: { icon: typeof Server; title: string; state?: { ok: boolean; detail: string } }) {
  return <Card title={title}><Icon className={state?.ok ? "mb-3 text-green-600" : "mb-3 text-slate-400"} /><Badge tone={state?.ok ? "success" : "danger"}>{state ? state.ok ? "healthy" : "unavailable" : "checking"}</Badge><p className="mt-2 text-sm text-slate-500">{state?.detail || "Checking..."}</p></Card>;
}
