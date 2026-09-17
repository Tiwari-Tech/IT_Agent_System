"use client";

import { Upload } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button, Input } from "@/components/ui/form";
import { EmptyState } from "@/components/ui/states";

export default function DocumentsPage() {
  const [file, setFile] = useState<File | null>(null);
  const valid = !file || ["pdf", "docx", "xlsx", "html", "txt"].includes(file.name.split(".").pop()?.toLowerCase() || "");
  return (
    <AppShell>
      <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
        <Card title="Upload document"><div className="space-y-4"><Input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} /><p className="text-sm text-slate-500">Supported: PDF, DOCX, XLSX, HTML, TXT. Upload and ingestion endpoints are pending.</p>{!valid && <p className="text-sm text-red-700">Unsupported file type.</p>}<Button disabled={!file || !valid}><Upload size={16} />Upload unavailable</Button></div></Card>
        <Card title="Knowledge base"><EmptyState title="Document API not available yet" detail="This page is ready for list, ingest, metadata, chunks, embeddings, and evidence search." /></Card>
      </div>
    </AppShell>
  );
}
