import { AlertCircle, Inbox } from "lucide-react";

export function EmptyState({ title, detail }: { title: string; detail?: string }) {
  return <div className="flex min-h-36 flex-col items-center justify-center rounded border border-dashed border-slate-300 p-6 text-center"><Inbox className="mb-2 text-slate-400" size={24} /><p className="font-medium text-slate-900">{title}</p>{detail && <p className="mt-1 max-w-md text-sm text-slate-500">{detail}</p>}</div>;
}

export function ErrorState({ title, detail }: { title: string; detail?: string }) {
  return <div className="rounded border border-red-200 bg-red-50 p-4 text-red-800"><div className="flex items-center gap-2 font-medium"><AlertCircle size={18} />{title}</div>{detail && <p className="mt-1 text-sm">{detail}</p>}</div>;
}
