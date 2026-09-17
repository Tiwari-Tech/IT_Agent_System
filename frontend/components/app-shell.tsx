"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity, Bell, Bot, CheckSquare, Database, FileText, Gauge, GitBranch, Home, LogOut, Menu, Shield, Ticket, UserCog, X } from "lucide-react";
import { useState } from "react";

import { AuthProvider, useAuth } from "@/lib/auth";

const nav = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/tickets", label: "Tickets", icon: Ticket },
  { href: "/assistant", label: "AI assistant", icon: Bot },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/approvals", label: "Approvals", icon: CheckSquare },
  { href: "/jira", label: "Jira", icon: GitBranch },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
  { href: "/admin", label: "Admin", icon: UserCog, admin: true },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return <AuthProvider><ShellInner>{children}</ShellInner></AuthProvider>;
}

function ShellInner({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const items = nav.filter((item) => !item.admin || user?.role === "it_admin");

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <aside className={`fixed inset-y-0 left-0 z-40 w-72 border-r border-slate-200 bg-white transition md:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4">
          <div className="flex items-center gap-2 font-semibold"><Shield className="text-blue-600" size={22} />IT Agent System</div>
          <button className="md:hidden" onClick={() => setOpen(false)}><X size={20} /></button>
        </div>
        <nav className="space-y-1 p-3">
          {items.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || (href !== "/" && pathname.startsWith(href));
            return <Link key={href} href={href} className={`flex items-center gap-3 rounded px-3 py-2 text-sm font-medium ${active ? "bg-blue-50 text-blue-700" : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"}`} onClick={() => setOpen(false)}><Icon size={18} />{label}</Link>;
          })}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 border-t border-slate-200 p-4">
          <div className="mb-3 text-sm"><p className="font-medium">{user?.name || "Not signed in"}</p><p className="text-slate-500">{user?.role || "Authenticate to use APIs"}</p></div>
          {user ? <button className="flex items-center gap-2 text-sm text-slate-600" onClick={() => { logout(); router.push("/login"); }}><LogOut size={16} />Logout</button> : <Link className="text-sm font-medium text-blue-700" href="/login">Login</Link>}
        </div>
      </aside>
      <div className="md:pl-72">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur">
          <div className="flex items-center gap-3"><button className="md:hidden" onClick={() => setOpen(true)}><Menu size={22} /></button><div><p className="text-xs text-slate-500">Enterprise IT operations</p><p className="font-semibold">{breadcrumb(pathname)}</p></div></div>
          <div className="flex items-center gap-3"><Database size={18} className="text-slate-500" /><Bell size={18} className="text-slate-500" /><Gauge size={18} className="text-slate-500" /></div>
        </header>
        <main className="p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}

function breadcrumb(pathname: string) {
  if (pathname === "/") return "Dashboard";
  return pathname.split("/").filter(Boolean).map((part) => part.replace("-", " ")).join(" / ");
}
