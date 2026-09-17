"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button, Select, Textarea } from "@/components/ui/form";
import { EmptyState, ErrorState } from "@/components/ui/states";
import { apiMessage, ticketsApi } from "@/lib/api";
import type { Message, Ticket } from "@/lib/types";

export default function TicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    ticketsApi.get(id).then(setTicket).catch((err) => setError(apiMessage(err)));
  }, [id]);

  async function patch(data: Partial<Ticket>) {
    try { setTicket(await ticketsApi.update(id, data)); } catch (err) { setError(apiMessage(err)); }
  }

  async function send() {
    if (!content.trim()) return;
    try { const message = await ticketsApi.message(id, content); setMessages([...messages, message]); setContent(""); } catch (err) { setError(apiMessage(err)); }
  }

  return (
    <AppShell>
      {error ? <ErrorState title="Ticket unavailable" detail={error} /> : !ticket ? <EmptyState title="Loading ticket" /> : (
        <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
          <div className="space-y-4">
            <Card title={ticket.title} action={<div className="flex gap-2"><Badge>{ticket.status}</Badge><Badge tone={ticket.priority === "critical" ? "danger" : ticket.priority === "high" ? "warning" : "neutral"}>{ticket.priority}</Badge></div>}>
              <p className="whitespace-pre-wrap text-slate-700">{ticket.description}</p>
              <div className="mt-4 grid gap-3 text-sm md:grid-cols-3"><Info label="Creator" value={ticket.creator?.name} /><Info label="Assignee" value={ticket.assignee?.name || "Unassigned"} /><Info label="Category" value={ticket.category || "None"} /></div>
            </Card>
            <Card title="Conversation">
              <div className="space-y-3">{messages.length === 0 && <EmptyState title="No messages loaded" detail="New messages you send in this session will appear here." />}{messages.map((message) => <div key={message.id} className="rounded border border-slate-200 p-3"><p className="text-xs text-slate-500">{message.role}</p><p>{message.content}</p></div>)}</div>
              <div className="mt-4 flex gap-2"><Textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Add a message" /><Button onClick={send}>Send</Button></div>
            </Card>
          </div>
          <div className="space-y-4">
            <Card title="Manage"><label className="text-sm font-medium">Status</label><Select className="mb-3" value={ticket.status} onChange={(e) => patch({ status: e.target.value as Ticket["status"] })}><option value="open">Open</option><option value="in_progress">In progress</option><option value="resolved">Resolved</option><option value="closed">Closed</option></Select><label className="text-sm font-medium">Priority</label><Select value={ticket.priority} onChange={(e) => patch({ priority: e.target.value as Ticket["priority"] })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></Select></Card>
            <Card title="AI workflow"><Workflow /></Card>
            <Card title="Audit activity"><EmptyState title="Audit API not available yet" detail="Ticket updates are audited by backend, but no read endpoint exists yet." /></Card>
          </div>
        </div>
      )}
    </AppShell>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="rounded bg-slate-50 p-3"><p className="text-slate-500">{label}</p><p className="font-medium">{value}</p></div>;
}

function Workflow() {
  return <ol className="space-y-3">{["Supervisor", "Diagnosis", "RAG", "Security", "Resolution", "Reviewer", "Ticket/Jira"].map((step, index) => <li key={step} className="flex items-center gap-3"><span className={`h-2.5 w-2.5 rounded-full ${index === 0 ? "bg-blue-600" : "bg-slate-300"}`} /><span className="text-sm">{step}</span><Badge>{index === 0 ? "ready" : "pending"}</Badge></li>)}</ol>;
}
