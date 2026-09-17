"use client";

import { useParams } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/states";

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  return <AppShell><Card title="Document details"><EmptyState title="Document endpoint unavailable" detail={`Document ${id} will show metadata, chunks, embeddings, and sources when backend APIs exist.`} /></Card></AppShell>;
}
