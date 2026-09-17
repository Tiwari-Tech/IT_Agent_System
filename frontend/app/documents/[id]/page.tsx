"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/states";
import { apiMessage, documentsApi } from "@/lib/api";
import type { DocumentItem } from "@/lib/types";

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [doc, setDoc] = useState<DocumentItem | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    documentsApi.get(id).then(setDoc).catch((err) => setError(apiMessage(err)));
  }, [id]);
  return (
    <AppShell>
      <Card title="Document details">
        {error ? <EmptyState title="Unable to load document" detail={error} /> : !doc ? <EmptyState title="Loading document" /> : (
          <div className="space-y-3 text-sm">
            <p className="text-lg font-semibold text-slate-950">{doc.title}</p>
            <p><span className="font-medium">Type:</span> {doc.file_type || "unknown"}</p>
            <p><span className="font-medium">Source:</span> {doc.source || "none"}</p>
            <p><span className="font-medium">Hash:</span> {doc.content_hash || "none"}</p>
            <p><span className="font-medium">Created:</span> {new Date(doc.created_at).toLocaleString()}</p>
          </div>
        )}
      </Card>
    </AppShell>
  );
}
