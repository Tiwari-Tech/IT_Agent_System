"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button, Input } from "@/components/ui/form";
import { AuthProvider, useAuth } from "@/lib/auth";

export default function LoginPage() {
  return <AuthProvider><LoginInner /></AuthProvider>;
}

function LoginInner() {
  const { login, error } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <form className="w-full max-w-sm rounded border border-slate-200 bg-white p-6" onSubmit={async (event) => { event.preventDefault(); setBusy(true); try { await login(email, password); router.push("/"); } finally { setBusy(false); } }}>
        <h1 className="text-xl font-semibold">Login</h1>
        <p className="mt-1 text-sm text-slate-500">Use your IT Agent System account.</p>
        <label className="mt-6 block text-sm font-medium">Email</label><Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        <label className="mt-4 block text-sm font-medium">Password</label><Input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        {error && <p className="mt-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        <Button className="mt-5 w-full" disabled={busy}>{busy ? "Signing in" : "Sign in"}</Button>
        <p className="mt-4 text-center text-sm text-slate-500">No account? <Link className="font-medium text-blue-700" href="/register">Register</Link></p>
      </form>
    </main>
  );
}
