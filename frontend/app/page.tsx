"use client";

import { Activity, AlertTriangle, Bot, CheckCircle2, Clock, Database, Server, TicketCheck } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/states";
import { useTickets } from "@/lib/hooks";

const priorityColors: Record<string, string> = { low: "#16a34a", medium: "#2563eb", high: "#f59e0b", critical: "#dc2626" };

export default function DashboardPage() {
  const { tickets, loading, error } = useTickets();
  const open = tickets.filter((ticket) => ticket.status === "open").length;
  const progress = tickets.filter((ticket) => ticket.status === "in_progress").length;
  const resolved = tickets.filter((ticket) => ticket.status === "resolved" || ticket.status === "closed").length;
  const high = tickets.filter((ticket) => ["high", "critical"].includes(ticket.priority)).length;
  const statusData = ["open", "in_progress", "resolved", "closed"].map((status) => ({ name: status.replace("_", " "), value: tickets.filter((ticket) => ticket.status === status).length }));
  const priorityData = ["low", "medium", "high", "critical"].map((priority) => ({ name: priority, value: tickets.filter((ticket) => ticket.priority === priority).length }));

  return (
    <AppShell>
      <div className="space-y-6">
        <div><p className="text-sm font-medium text-slate-500">Operations overview</p><h1 className="text-2xl font-semibold text-slate-950">IT command center</h1></div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Metric icon={TicketCheck} label="Total tickets" value={tickets.length} />
          <Metric icon={AlertTriangle} label="Open" value={open} tone="amber" />
          <Metric icon={Clock} label="In progress" value={progress} tone="blue" />
          <Metric icon={CheckCircle2} label="Resolved" value={resolved} tone="green" />
        </div>
        <div className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
          <Card title="Ticket status"><div className="h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={statusData}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div></Card>
          <Card title="Priority mix"><div className="h-72"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={priorityData} dataKey="value" nameKey="name" outerRadius={92} label>{priorityData.map((entry) => <Cell key={entry.name} fill={priorityColors[entry.name]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></div></Card>
        </div>
        <div className="grid gap-4 xl:grid-cols-[1.3fr_.9fr]">
          <Card title="Recent tickets">
            {loading ? <EmptyState title="Loading tickets" /> : error ? <EmptyState title="Ticket API unavailable" detail={error} /> : tickets.length === 0 ? <EmptyState title="No tickets yet" detail="Create a ticket to populate the operations view." /> : (
              <div className="divide-y divide-slate-200">{tickets.slice(0, 6).map((ticket) => <div key={ticket.id} className="flex items-center justify-between gap-4 py-3"><div><p className="font-medium text-slate-900">{ticket.title}</p><p className="text-sm text-slate-500">{ticket.category || "Uncategorized"} · {ticket.creator?.name}</p></div><div className="flex gap-2"><Badge>{ticket.status}</Badge><Badge tone={ticket.priority === "critical" || ticket.priority === "high" ? "danger" : "neutral"}>{ticket.priority}</Badge></div></div>)}</div>
            )}
          </Card>
          <Card title="System health">
            <div className="grid gap-3">
              <Health icon={Server} label="API" value="Connected when /health responds" />
              <Health icon={Database} label="PostgreSQL" value="Uses /health/db" />
              <Health icon={Activity} label="Redis/Valkey" value="Uses /health/redis" />
              <Health icon={Bot} label="Agents" value="Runs from ticket workflow" />
            </div>
            <div className="mt-4 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">{high} high-priority tickets need attention.</div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

function Metric({ icon: Icon, label, value, tone = "slate" }: { icon: typeof TicketCheck; label: string; value: number; tone?: "slate" | "amber" | "blue" | "green" }) {
  const color = { slate: "text-slate-600 bg-slate-100", amber: "text-amber-700 bg-amber-100", blue: "text-blue-700 bg-blue-100", green: "text-green-700 bg-green-100" }[tone];
  return <div className="rounded border border-slate-200 bg-white p-4"><div className={`mb-4 flex h-9 w-9 items-center justify-center rounded ${color}`}><Icon size={18} /></div><p className="text-sm text-slate-500">{label}</p><p className="text-3xl font-semibold text-slate-950">{value}</p></div>;
}

function Health({ icon: Icon, label, value, muted }: { icon: typeof Server; label: string; value: string; muted?: boolean }) {
  return <div className="flex items-center gap-3 rounded border border-slate-200 p-3"><Icon className={muted ? "text-slate-400" : "text-green-600"} size={18} /><div><p className="font-medium text-slate-900">{label}</p><p className="text-sm text-slate-500">{value}</p></div></div>;
}
