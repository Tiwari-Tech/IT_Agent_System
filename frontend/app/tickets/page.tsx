"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button, Input, Select } from "@/components/ui/form";
import { EmptyState, ErrorState } from "@/components/ui/states";
import { useTickets } from "@/lib/hooks";

export default function TicketsPage() {
  const [filters, setFilters] = useState({ status: "", priority: "", category: "", search: "" });
  const params = useMemo(() => ({ page: 1, limit: 50, status: filters.status || undefined, priority: filters.priority || undefined, category: filters.category || undefined }), [filters]);
  const { tickets, total, loading, error } = useTickets(params);
  const visible = tickets.filter((ticket) => ticket.title.toLowerCase().includes(filters.search.toLowerCase()) || ticket.description.toLowerCase().includes(filters.search.toLowerCase()));
  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center"><div><h1 className="text-2xl font-semibold">Tickets</h1><p className="text-sm text-slate-500">{total} total tickets from backend</p></div><Link href="/tickets/new"><Button>New ticket</Button></Link></div>
        <div className="grid gap-3 rounded border border-slate-200 bg-white p-3 md:grid-cols-4"><Input placeholder="Search" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} /><Select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}><option value="">All statuses</option><option value="open">Open</option><option value="in_progress">In progress</option><option value="resolved">Resolved</option><option value="closed">Closed</option></Select><Select value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}><option value="">All priorities</option><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></Select><Input placeholder="Category" value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })} /></div>
        {error ? <ErrorState title="Unable to load tickets" detail={error} /> : loading ? <EmptyState title="Loading tickets" /> : visible.length === 0 ? <EmptyState title="No tickets found" /> : <div className="overflow-hidden rounded border border-slate-200 bg-white"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500"><tr><th className="p-3">Ticket</th><th>Status</th><th>Priority</th><th>Owner</th><th>Updated</th></tr></thead><tbody className="divide-y divide-slate-200">{visible.map((ticket) => <tr key={ticket.id} className="hover:bg-slate-50"><td className="p-3"><Link className="font-medium text-blue-700" href={`/tickets/${ticket.id}`}>{ticket.title}</Link><p className="text-slate-500">{ticket.category || "Uncategorized"}</p></td><td><Badge>{ticket.status}</Badge></td><td><Badge tone={ticket.priority === "critical" ? "danger" : ticket.priority === "high" ? "warning" : "neutral"}>{ticket.priority}</Badge></td><td>{ticket.creator?.name}</td><td>{new Date(ticket.updated_at).toLocaleString()}</td></tr>)}</tbody></table></div>}
      </div>
    </AppShell>
  );
}
