export function Card({ title, action, children }: { title?: string; action?: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="rounded border border-slate-200 bg-white">
      {(title || action) && <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3"><h2 className="font-semibold text-slate-950">{title}</h2>{action}</div>}
      <div className="p-4">{children}</div>
    </section>
  );
}
