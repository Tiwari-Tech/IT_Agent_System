"use client";

import { Activity, FileClock, ShieldAlert, Users } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/states";
import { useAuth } from "@/lib/auth";

export default function AdminPage() {
  return <AppShell><AdminInner /></AppShell>;
}

function AdminInner() {
  const { user } = useAuth();
  if (user && user.role !== "it_admin") return <div className="rounded border border-red-200 bg-red-50 p-4 text-red-800"><ShieldAlert className="mb-2" />Access denied. IT admin role required.</div>;
  return (
    <div className="space-y-4">
      <div><h1 className="text-2xl font-semibold">Admin</h1><p className="text-sm text-slate-500">Administrative views for users, agent runs, audit logs, and runtime configuration.</p></div>
    <div className="grid gap-4 xl:grid-cols-3">
      <AdminCard icon={Users} title="Users" detail="User list, active/inactive state, and role management need admin backend endpoints." />
      <AdminCard icon={Activity} title="Agent runs" detail="Existing table is ready; read/filter endpoints are future work." />
      <AdminCard icon={FileClock} title="Audit logs" detail="Ticket mutations write audit logs; admin listing endpoint is pending." />
      <Card title="System configuration"><div className="grid gap-2"><Badge>JWT enabled</Badge><Badge>RBAC enabled</Badge><Badge>Ollama configured</Badge><Badge>PostgreSQL + Redis</Badge></div></Card>
      <Card title="Security posture"><div className="space-y-2 text-sm text-slate-600"><p>Secrets are never displayed in the UI.</p><p>Admin-only panels are hidden from non-admin navigation.</p><p>Unavailable integrations render disabled controls.</p></div></Card>
      <Card title="Access model"><div className="space-y-2"><Badge>employee</Badge><Badge>it_support</Badge><Badge>it_admin</Badge></div></Card>
    </div>
    </div>
  );
}

function AdminCard({ icon: Icon, title, detail }: { icon: typeof Users; title: string; detail: string }) {
  return <Card title={title}><div className="mb-4 flex h-10 w-10 items-center justify-center rounded bg-blue-50 text-blue-700"><Icon size={18} /></div><EmptyState title={`${title} API pending`} detail={detail} /></Card>;
}
