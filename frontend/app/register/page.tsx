"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button, Input, Select } from "@/components/ui/form";
import { AuthProvider, useAuth } from "@/lib/auth";

export default function RegisterPage() {
  return <AuthProvider><RegisterInner /></AuthProvider>;
}

function RegisterInner() {
  const { register, error } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "employee" });
  const [busy, setBusy] = useState(false);
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <form className="w-full max-w-md rounded border border-slate-200 bg-white p-6" onSubmit={async (event) => { event.preventDefault(); setBusy(true); try { await register(form); router.push("/"); } finally { setBusy(false); } }}>
        <h1 className="text-xl font-semibold">Create account</h1>
        <label className="mt-6 block text-sm font-medium">Name</label><Input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        <label className="mt-4 block text-sm font-medium">Email</label><Input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
        <label className="mt-4 block text-sm font-medium">Password</label><Input type="password" minLength={8} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
        <label className="mt-4 block text-sm font-medium">Role</label><Select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })}><option value="employee">Employee</option><option value="it_support">IT support</option><option value="it_admin">IT admin</option></Select>
        {error && <p className="mt-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        <Button className="mt-5 w-full" disabled={busy}>{busy ? "Creating" : "Create account"}</Button>
        <p className="mt-4 text-center text-sm text-slate-500">Already registered? <Link className="font-medium text-blue-700" href="/login">Login</Link></p>
      </form>
    </main>
  );
}
