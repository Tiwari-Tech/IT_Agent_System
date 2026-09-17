"use client";

import { ExternalLink, GitBranch, Link2, MessageSquare, RefreshCw } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button, Input } from "@/components/ui/form";
import { EmptyState } from "@/components/ui/states";
import { apiMessage, jiraApi } from "@/lib/api";

export default function JiraPage() {
  const [issueKey, setIssueKey] = useState("");
  const [status, setStatus] = useState("");
  async function fetchIssue() {
    try {
      const result = await jiraApi.getIssue(issueKey);
      setStatus(`Loaded ${String(result.data.key || issueKey)}`);
    } catch (err) { setStatus(apiMessage(err)); }
  }
  return (
    <AppShell>
      <div className="space-y-4">
        <div><h1 className="text-2xl font-semibold">Jira integration</h1><p className="text-sm text-slate-500">Create, link, sync, and comment flows are prepared for the future backend integration.</p></div>
      <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
        <Card title="Create or link issue"><div className="space-y-3"><Input value={issueKey} onChange={(event) => setIssueKey(event.target.value.toUpperCase())} placeholder="Jira issue key, e.g. IT-123" /><div className="grid grid-cols-2 gap-2"><Button disabled><Link2 size={16} />Link</Button><Button disabled variant="secondary"><GitBranch size={16} />Create</Button></div><Button disabled={!issueKey} onClick={fetchIssue}>Fetch issue</Button><p className="text-sm text-slate-500">{status || "Uses backend Jira routes when configured."}</p></div></Card>
        <Card title="Linked issue" action={<Badge>{issueKey || "none"}</Badge>}>
          {issueKey ? <div className="space-y-3"><Row icon={ExternalLink} label="Issue key" value={issueKey} /><Row icon={RefreshCw} label="Sync status" value={status || "Ready"} /><Row icon={MessageSquare} label="Comments" value="Use backend comment API" /><Button disabled variant="secondary"><RefreshCw size={16} />Ticket sync requires ticket context</Button></div> : <EmptyState title="No Jira issue selected" detail="Enter an issue key to preview integration state." />}
        </Card>
      </div>
      </div>
    </AppShell>
  );
}

function Row({ icon: Icon, label, value }: { icon: typeof ExternalLink; label: string; value: string }) {
  return <div className="flex items-center gap-3 rounded border border-slate-200 p-3"><Icon className="text-slate-500" size={17} /><div><p className="text-sm font-medium">{label}</p><p className="text-sm text-slate-500">{value}</p></div></div>;
}
