"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button, Input, Select, Textarea } from "@/components/ui/form";
import { apiMessage, ticketsApi } from "@/lib/api";

export default function NewTicketPage() {
  const router = useRouter();
  const [form, setForm] = useState({ title: "", description: "", priority: "medium", status: "open", category: "" });
  const [error, setError] = useState("");
  return (
    <AppShell>
      <Card title="Create ticket">
        <form className="max-w-2xl space-y-4" onSubmit={async (event) => { event.preventDefault(); try { const ticket = await ticketsApi.create(form); router.push(`/tickets/${ticket.id}`); } catch (err) { setError(apiMessage(err)); } }}>
          <div><label className="text-sm font-medium">Title</label><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
          <div><label className="text-sm font-medium">Description</label><Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required /></div>
          <div className="grid gap-3 md:grid-cols-3"><Select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></Select><Select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}><option value="open">Open</option><option value="in_progress">In progress</option></Select><Input placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /></div>
          {error && <p className="rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}<Button>Create ticket</Button>
        </form>
      </Card>
    </AppShell>
  );
}
