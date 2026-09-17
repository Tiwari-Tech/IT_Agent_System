"use client";

import { AlertTriangle, CheckCircle2, Clock, FileText, RotateCcw, ShieldAlert, XCircle } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/form";

export default function ApprovalsPage() {
  const sample = [
    { id: "APP-1024", risk: "critical", title: "Privileged remediation requires approval", ticket: "VPN outage for finance team", resolution: "Rotate affected VPN gateway certificate and restart the gateway during a five-minute maintenance window.", rollback: "Restore previous certificate bundle and restart gateway.", evidence: "Supervisor marked external access impact; security agent requires human approval." },
    { id: "APP-1025", risk: "medium", title: "Restart service during maintenance window", ticket: "Intermittent print service failures", resolution: "Restart print spooler and clear stuck jobs after business hours.", rollback: "Revert queue state from backup snapshot.", evidence: "Diagnosis confidence medium; no privileged data access required." },
  ];
  const [selected, setSelected] = useState(sample[0]);
  return (
    <AppShell>
      <div className="space-y-4">
        <div><h1 className="text-2xl font-semibold">Approvals</h1><p className="text-sm text-slate-500">Human approval queue for high-risk automation. Backend approval actions are pending.</p></div>
      <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
        <Card title="Pending approvals">
          <div className="space-y-3">{sample.map((item) => <button key={item.id} onClick={() => setSelected(item)} className={`w-full rounded border p-4 text-left ${selected.id === item.id ? "border-blue-400 bg-blue-50" : "border-slate-200 bg-white hover:bg-slate-50"}`}><div className="flex items-center justify-between gap-3"><p className="font-medium">{item.title}</p><Badge tone={item.risk === "critical" ? "danger" : "warning"}>{item.risk}</Badge></div><p className="mt-1 text-sm text-slate-500">{item.ticket}</p><div className="mt-3 flex items-center gap-2 text-xs text-slate-500"><Clock size={14} />waiting for approval</div></button>)}</div>
        </Card>
        <Card title="Approval detail" action={<Badge tone={selected.risk === "critical" ? "danger" : "warning"}>{selected.id}</Badge>}>
          <div className="space-y-4">
            <Panel icon={FileText} label="Proposed resolution" text={selected.resolution} />
            <Panel icon={AlertTriangle} label="Evidence" text={selected.evidence} />
            <Panel icon={RotateCcw} label="Rollback" text={selected.rollback} />
            <div className="rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900"><ShieldAlert size={16} className="mb-1" />Approval and rejection calls are disabled until the backend workflow API exists.</div>
            <div className="flex gap-2"><Button disabled><CheckCircle2 size={16} />Approve</Button><Button disabled variant="secondary"><XCircle size={16} />Reject</Button></div>
          </div>
        </Card>
      </div>
      </div>
    </AppShell>
  );
}

function Panel({ icon: Icon, label, text }: { icon: typeof FileText; label: string; text: string }) {
  return <div className="rounded border border-slate-200 p-3"><p className="mb-1 flex items-center gap-2 text-sm font-medium text-slate-900"><Icon size={16} />{label}</p><p className="text-sm text-slate-600">{text}</p></div>;
}
