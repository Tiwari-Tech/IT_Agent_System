"use client";

import { Upload } from "lucide-react";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button, Input } from "@/components/ui/form";
import { EmptyState } from "@/components/ui/states";
import { apiMessage, documentsApi } from "@/lib/api";
import type { DocumentItem } from "@/lib/types";

export default function DocumentsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [message, setMessage] = useState("");
  const valid = !file || ["pdf", "docx", "xlsx", "html", "txt"].includes(file.name.split(".").pop()?.toLowerCase() || "");
  useEffect(() => { documentsApi.list().then((data) => setDocs(data.items)).catch((err) => setMessage(apiMessage(err))); }, []);
  async function upload() {
    if (!file || !valid) return;
    try {
      const doc = await documentsApi.upload(file);
      setDocs([doc, ...docs]);
      setMessage("Uploaded");
    } catch (err) { setMessage(apiMessage(err)); }
  }
  async function ingest(id: string) {
    try {
      const result = await documentsApi.ingest(id);
      setMessage(`Ingested ${result.chunks} chunks`);
    } catch (err) { setMessage(apiMessage(err)); }
  }
  return (
    <AppShell>
      <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
        <Card title="Upload document"><div className="space-y-4"><Input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} /><p className="text-sm text-slate-500">Supported: PDF, DOCX, XLSX, HTML, TXT.</p>{!valid && <p className="text-sm text-red-700">Unsupported file type.</p>}<Button disabled={!file || !valid} onClick={upload}><Upload size={16} />Upload</Button>{message && <p className="text-sm text-slate-600">{message}</p>}</div></Card>
        <Card title="Knowledge base">{docs.length === 0 ? <EmptyState title="No documents" detail={message || "Upload a document to start ingestion."} /> : <div className="space-y-3">{docs.map((doc) => <div key={doc.id} className="rounded border border-slate-200 p-3"><p className="font-medium">{doc.title}</p><p className="text-sm text-slate-500">{doc.file_type} · {doc.content_hash?.slice(0, 12)}</p><Button className="mt-2" variant="secondary" onClick={() => ingest(doc.id)}>Ingest</Button></div>)}</div>}</Card>
      </div>
    </AppShell>
  );
}
