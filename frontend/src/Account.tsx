import { useEffect, useState } from "react";
import { authHeader, getSession, signIn, signOut, signUp } from "./auth";
const API = import.meta.env.VITE_API_URL ?? "";
type Me = { tier: string; used: number; limit: number };
export default function Account({ onChange }: { onChange: () => void }) {
  const s = getSession();
  const [email, setEmail] = useState(""), [pw, setPw] = useState(""), [msg, setMsg] = useState(""), [busy, setBusy] = useState(false), [me, setMe] = useState<Me | null>(null);
  useEffect(() => {
    authHeader().then(h => fetch(API + "/api/me", { headers: h })).then(r => r.json()).then(setMe).catch(() => {});
  }, []);
  async function go(up: boolean) {
    setBusy(true); setMsg("");
    try { const r = up ? await signUp(email, pw) : await signIn(email, pw); if (r) onChange(); else setMsg("Check your email to confirm your account, then sign in."); }
    catch (e) { setMsg((e as Error).message); } finally { setBusy(false); }
  }
  async function upgrade(tier: string) {
    setMsg("");
    const r = await fetch(`${API}/api/billing/checkout?tier=${tier}`, { headers: await authHeader() });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) return setMsg(j.detail || "Could not start checkout.");
    const f = document.createElement("form"); f.method = "POST"; f.action = j.action;
    Object.entries(j.fields).forEach(([k, v]) => { const i = document.createElement("input"); i.type = "hidden"; i.name = k; i.value = String(v); f.appendChild(i); });
    document.body.appendChild(f); f.submit();
  }
  return (
    <section className="card">
      <p className="mono eyebrow">Your kitchen</p>
      {s ? <>
        <h2 className="serif">{s.email}</h2>
        {me && <p className="lede">{me.tier[0].toUpperCase() + me.tier.slice(1)} plan · {me.used} of {me.limit > 1000 ? "unlimited" : me.limit} recipes today</p>}
        {me?.tier !== "premium" && <div className="row"><button className="ghost" onClick={() => upgrade("basic")}>Basic · R15/month</button><button className="ghost" onClick={() => upgrade("premium")}>Premium · R99/month</button></div>}
        <button className="link" onClick={() => { signOut(); onChange(); }}>Sign out</button>
      </> : <>
        <h2 className="serif">Save your recipes</h2>
        <label>Email<input type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" autoComplete="current-password" value={pw} onChange={e => setPw(e.target.value)} /></label>
        <div className="row">
          <button className="ghost" disabled={busy || !email || pw.length < 6} onClick={() => go(false)}>Sign in</button>
          <button className="ghost" disabled={busy || !email || pw.length < 6} onClick={() => go(true)}>Create account</button>
        </div>
      </>}
      {msg && <p className="err" role="alert">{msg}</p>}
    </section>
  );
}
