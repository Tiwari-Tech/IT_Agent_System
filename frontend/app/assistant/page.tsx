"use client";

import { Bot, Send, Square } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button, Textarea } from "@/components/ui/form";
import { EmptyState } from "@/components/ui/states";

type ChatMessage = { role: "user" | "assistant"; content: string };

export default function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState("");
  function send() {
    if (!text.trim()) return;
    setMessages([...messages, { role: "user", content: text }, { role: "assistant", content: "The WebSocket endpoint is not available yet. This panel is ready to stream safe agent progress and final responses when /api/v1/ws/chat is implemented." }]);
    setText("");
  }
  return (
    <AppShell>
      <div className="grid gap-4 xl:grid-cols-[1fr_340px]">
        <Card title="AI IT support assistant" action={<Badge>WebSocket pending</Badge>}>
          <div className="min-h-[460px] space-y-3">{messages.length === 0 ? <EmptyState title="No conversation yet" detail="Ask about a ticket, outage, access issue, or troubleshooting plan." /> : messages.map((message, index) => <div key={index} className={`rounded p-3 ${message.role === "user" ? "ml-auto max-w-xl bg-blue-600 text-white" : "max-w-xl border border-slate-200 bg-white text-slate-800"}`}>{message.content}</div>)}</div>
          <div className="mt-4 flex gap-2"><Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Describe the IT issue..." /><div className="space-y-2"><Button onClick={send}><Send size={16} />Send</Button><Button variant="secondary"><Square size={16} />Stop</Button></div></div>
        </Card>
        <Card title="Agent status"><div className="space-y-3">{["Supervisor", "Diagnosis", "RAG", "Security", "Resolution", "Reviewer"].map((agent) => <div key={agent} className="flex items-center justify-between rounded border border-slate-200 p-3"><span className="flex items-center gap-2"><Bot size={16} />{agent}</span><Badge>pending</Badge></div>)}</div></Card>
      </div>
    </AppShell>
  );
}
