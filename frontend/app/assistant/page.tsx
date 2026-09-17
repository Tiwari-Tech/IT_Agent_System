"use client";

import { Bot, Send, Square } from "lucide-react";
import { useRef, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button, Textarea } from "@/components/ui/form";
import { EmptyState } from "@/components/ui/states";
import { createChatSocket, getToken } from "@/lib/api";

type ChatMessage = { role: "user" | "assistant"; content: string };

export default function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState("");
  const [ticketId, setTicketId] = useState("");
  const [status, setStatus] = useState("disconnected");
  const socket = useRef<WebSocket | null>(null);
  function send() {
    if (!text.trim() || !ticketId.trim()) return;
    const next = [...messages, { role: "user" as const, content: text }];
    setMessages(next);
    if (!socket.current || socket.current.readyState !== WebSocket.OPEN) {
      socket.current = createChatSocket(getToken());
      socket.current.onopen = () => {
        setStatus("connected");
        socket.current?.send(JSON.stringify({ ticket_id: ticketId, message: text }));
      };
      socket.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "final_response") setMessages((items) => [...items, { role: "assistant", content: data.result?.resolution_plan || "Workflow completed." }]);
        else if (data.type === "error") setMessages((items) => [...items, { role: "assistant", content: data.message }]);
        else setStatus(data.type);
      };
      socket.current.onclose = () => setStatus("disconnected");
    } else {
      socket.current.send(JSON.stringify({ ticket_id: ticketId, message: text }));
    }
    setText("");
  }
  return (
    <AppShell>
      <div className="grid gap-4 xl:grid-cols-[1fr_340px]">
        <Card title="AI IT support assistant" action={<Badge>{status}</Badge>}>
          <div className="min-h-[460px] space-y-3">{messages.length === 0 ? <EmptyState title="No conversation yet" detail="Ask about a ticket, outage, access issue, or troubleshooting plan." /> : messages.map((message, index) => <div key={index} className={`rounded p-3 ${message.role === "user" ? "ml-auto max-w-xl bg-blue-600 text-white" : "max-w-xl border border-slate-200 bg-white text-slate-800"}`}>{message.content}</div>)}</div>
          <input className="mt-4 h-10 w-full rounded border border-slate-300 px-3 text-sm" value={ticketId} onChange={(e) => setTicketId(e.target.value)} placeholder="Ticket ID" />
          <div className="mt-3 flex gap-2"><Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Describe the IT issue..." /><div className="space-y-2"><Button onClick={send}><Send size={16} />Send</Button><Button variant="secondary" onClick={() => socket.current?.close()}><Square size={16} />Stop</Button></div></div>
        </Card>
        <Card title="Agent status"><div className="space-y-3">{["Supervisor", "Diagnosis", "RAG", "Security", "Resolution", "Reviewer"].map((agent) => <div key={agent} className="flex items-center justify-between rounded border border-slate-200 p-3"><span className="flex items-center gap-2"><Bot size={16} />{agent}</span><Badge>pending</Badge></div>)}</div></Card>
      </div>
    </AppShell>
  );
}
