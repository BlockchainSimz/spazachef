import { useEffect, useState, type FormEvent } from "react";
const API = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");
const SUPABASE_URL = (import.meta.env.VITE_SUPABASE_URL ?? "").replace(/\/$/, "");
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY ?? "";
type Session = { access_token: string; refresh_token: string; expires_at?: number; user?: { email?: string } };
const readSession = (): Session | null => { try { return JSON.parse(localStorage.getItem("supabase_session") || "null"); } catch { return null; } };
const saveSession = (session: Session) => { localStorage.setItem("supabase_session", JSON.stringify(session)); localStorage.setItem("token", session.access_token); };
async function refreshSession(): Promise<boolean> {
  const current = readSession();
  if (!current?.refresh_token || !SUPABASE_URL || !SUPABASE_KEY) return false;
  const response = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=refresh_token`, { method: "POST", headers: { "Content-Type": "application/json", apikey: SUPABASE_KEY }, body: JSON.stringify({ refresh_token: current.refresh_token }) });
  if (!response.ok) { localStorage.removeItem("supabase_session"); localStorage.removeItem("token"); return false; }
  const value = await response.json(); saveSession({ ...value, expires_at: Date.now() + (value.expires_in ?? 3600) * 1000 }); return true;
}
const PERSONAS = [
  { id: "zanele", ini: "AZ", name: "Auntie Zanele", tag: "Comfort food, big flavour", bio: "Generous, warm, and deeply practical. She knows how to stretch a pantry." },
  { id: "jabu", ini: "BJ", name: "Braai Boss Jabu", tag: "Fire, smoke, and confidence", bio: "Bold and direct, with a soft spot for clever shortcuts and a good char." },
  { id: "farah", ini: "CF", name: "Chef Farah", tag: "Spice with a story", bio: "Bright, aromatic, and precise, bringing Cape Malay warmth to every pot." },
  { id: "raj", ini: "RN", name: "Raj from next door", tag: "Clever swaps, no fuss", bio: "Playful and resourceful, turning everyday ingredients into something worth sharing." },
];
type Recipe = { id: string; title: string; persona_name: string; intro: string; serves: number; minutes: number; ingredients: { item: string; amount: string }[]; steps: string[]; notes: string[]; rating?: number | null; cooked?: boolean };
const uid = (): Record<string, string> => { const t = localStorage.getItem("token"); return t ? { Authorization: `Bearer ${t}` } : {}; };
async function api<T>(path: string, body?: unknown): Promise<T> {
  let r = await fetch(API + path, { method: body ? "POST" : "GET", headers: { "Content-Type": "application/json", ...uid() }, body: body ? JSON.stringify(body) : undefined });
  if (r.status === 401 && await refreshSession()) r = await fetch(API + path, { method: body ? "POST" : "GET", headers: { "Content-Type": "application/json", ...uid() }, body: body ? JSON.stringify(body) : undefined });
  const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(typeof j.detail === "string" ? j.detail : "Something went wrong. Try again.");
  return j;
}
export default function App() {
  const [persona, setPersona] = useState("zanele"), [ing, setIng] = useState(""), [diet, setDiet] = useState(""), [serves, setServes] = useState(4), [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false), [err, setErr] = useState(""), [recipe, setRecipe] = useState<Recipe | null>(null), [recent, setRecent] = useState<Recipe[]>([]), [all, setAll] = useState(false);
  const [online, setOnline] = useState(navigator.onLine);
  const [session, setSession] = useState<Session | null>(() => readSession());
  const [email, setEmail] = useState(() => readSession()?.user?.email ?? ""), [password, setPassword] = useState(""), [authMode, setAuthMode] = useState<"signin" | "signup">("signin"), [authBusy, setAuthBusy] = useState(false), [authErr, setAuthErr] = useState("");
  const [checkoutBusy, setCheckoutBusy] = useState(false), [checkoutErr, setCheckoutErr] = useState("");
  async function authenticate(e: FormEvent) {
    e.preventDefault(); setAuthBusy(true); setAuthErr("");
    try {
      const signup = authMode === "signup";
      const response = await fetch(`${SUPABASE_URL}/auth/v1/${signup ? "signup" : "token?grant_type=password"}`, { method: "POST", headers: { "Content-Type": "application/json", apikey: SUPABASE_KEY }, body: JSON.stringify({ email, password }) });
      const value = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(value.msg || value.message || value.error_description || "Sign in failed. Check your details and try again.");
      if (!value.access_token) { setAuthErr("Check your email to confirm your account, then sign in."); setAuthMode("signin"); return; }
      const next = { ...value, expires_at: Date.now() + (value.expires_in ?? 3600) * 1000 } as Session; saveSession(next); setSession(next);
    } catch (error) { setAuthErr((error as Error).message); } finally { setAuthBusy(false); }
  }
  function signOut() { localStorage.removeItem("supabase_session"); localStorage.removeItem("token"); localStorage.removeItem("recent"); setRecent([]); setRecipe(null); setEmail(""); setSession(null); }
  async function startCheckout(tier: "basic" | "premium") {
    setCheckoutBusy(true); setCheckoutErr("");
    try {
      const checkout = await api<{ action: string; fields: Record<string, string> }>("/api/payfast/checkout", { tier, email });
      const target = new URL(checkout.action);
      const allowedHosts = ["www.payfast.co.za", "sandbox.payfast.co.za"];
      if (target.protocol !== "https:" || !allowedHosts.includes(target.hostname) || target.pathname !== "/eng/process") throw new Error("Checkout destination could not be verified.");
      const form = document.createElement("form"); form.method = "POST"; form.action = target.toString(); form.style.display = "none";
      Object.entries(checkout.fields).forEach(([name, value]) => { const input = document.createElement("input"); input.type = "hidden"; input.name = name; input.value = value; form.appendChild(input); });
      document.body.appendChild(form); form.submit();
    } catch (error) { setCheckoutErr((error as Error).message); setCheckoutBusy(false); }
  }
  useEffect(() => { const f = () => setOnline(navigator.onLine); addEventListener("online", f); addEventListener("offline", f); return () => { removeEventListener("online", f); removeEventListener("offline", f); }; }, []);
  useEffect(() => { api<Recipe[]>("/api/recipes").then(r => { setRecent(r); localStorage.setItem("recent", JSON.stringify(r)); }).catch(() => setRecent(JSON.parse(localStorage.getItem("recent") || "[]"))); }, [session?.access_token]);
  async function go(regen = false) {
    if (regen && recipe) api(`/api/recipes/${recipe.id}/feedback`, { regenerated: true }).catch(() => {});
    setBusy(true); setErr("");
    try { const r = await api<Recipe>("/api/recipes/generate", { persona, ingredients: ing, diet, serves, notes }); setRecipe(r); setRecent(x => [r, ...x]); setTimeout(() => document.getElementById("result")?.scrollIntoView({ behavior: "smooth" }), 50); }
    catch (e) { setErr(!online ? "You're offline. Your saved recipes are still below." : (e as Error).message); } finally { setBusy(false); }
  }
  const rate = (r: Recipe, rating?: number, cooked = false) => { api(`/api/recipes/${r.id}/feedback`, { rating, cooked }).catch(() => {}); const u = { ...r, rating: rating ?? r.rating, cooked: cooked || r.cooked }; setRecipe(u); setRecent(x => x.map(y => y.id === r.id ? u : y)); };
  const shown = all ? recent : recent.slice(0, 3);
  return (<>
    <header className="top"><div className="logo" aria-hidden>👨‍🍳</div><div><b className="serif brand">SpazaChef</b><small className="mono">Cook what's here</small></div><button className="icon" aria-label="Menu">☰</button></header>
    <main>
      {SUPABASE_URL && SUPABASE_KEY && !session ? <section className="card"><p className="mono eyebrow">Your kitchen, saved</p><h1 className="serif">Sign in to <em>SpazaChef</em></h1><form onSubmit={authenticate}><label>Email<input type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} /></label><label>Password<input type="password" autoComplete={authMode === "signin" ? "current-password" : "new-password"} minLength={8} required value={password} onChange={e => setPassword(e.target.value)} /></label>{authErr && <p className="err" role="alert">{authErr}</p>}<button className="cta" disabled={authBusy}>{authBusy ? "Please wait…" : authMode === "signin" ? "Sign in" : "Create account"}</button></form><button className="link" onClick={() => { setAuthMode(authMode === "signin" ? "signup" : "signin"); setAuthErr(""); }}>{authMode === "signin" ? "New here? Create an account" : "Already have an account? Sign in"}</button></section> : <>
      {session && <button className="link" onClick={signOut}>Sign out</button>}
      {!online && <p className="banner" role="status">Offline mode: saved recipes are available.</p>}
      <span className="pill mono">Supper, sorted</span>
      <h1 className="serif">What's in the <em>spaza?</em></h1>
      <p className="lede">Tell us what's on hand. We'll turn it into something worth sitting down for.</p>
      <section className="card"><p className="mono eyebrow">01 / Choose a voice</p><h2 className="serif">Who's cooking with you?</h2>
        <div role="radiogroup" aria-label="Chef voice">{PERSONAS.map(p => <button key={p.id} role="radio" aria-checked={persona === p.id} className={"persona" + (persona === p.id ? " on" : "")} onClick={() => setPersona(p.id)}>
          <span className="ini serif">{p.ini}</span>{persona === p.id && <span className="sel mono">Selected</span>}<b className="serif">{p.name}</b><span className="tag">{p.tag}</span><span className="bio mono">{p.bio}</span></button>)}</div></section>
      <section className="card"><p className="mono eyebrow">02 / Build your brief</p><h2 className="serif">Open the cupboard</h2>
        <label>Ingredients, one line or comma apart<textarea rows={5} value={ing} onChange={e => setIng(e.target.value)} placeholder="rice, tinned tomatoes, one onion…" /></label>
        <div className="row"><label>Dietary preference <i>optional</i><input value={diet} onChange={e => setDiet(e.target.value)} placeholder="e.g. vegetarian" /></label>
          <div className="lab">Serves<div className="step"><button aria-label="Fewer" onClick={() => setServes(Math.max(1, serves - 1))}>−</button><span>{serves}</span><button aria-label="More" onClick={() => setServes(Math.min(20, serves + 1))}>+</button></div></div></div>
        <label>Pantry notes <i>optional</i><input value={notes} onChange={e => setNotes(e.target.value)} placeholder="Keep it mild; no oven tonight" /></label>
        {err && <p className="err" role="alert">{err}</p>}
        <button className="cta" disabled={busy || ing.trim().length < 2} onClick={() => go()}>{busy ? "Cooking up ideas…" : "Cook with what I have"}</button></section>
      {recipe && <section id="result" className="card recipe"><p className="mono eyebrow">{recipe.persona_name}</p><h2 className="serif">{recipe.title}</h2><p className="lede">“{recipe.intro}”</p>
        <p className="mono eyebrow">{recipe.minutes} min · serves {recipe.serves}</p>
        <h3 className="serif">Ingredients</h3><ul>{recipe.ingredients.map((i, k) => <li key={k}><b>{i.amount}</b> {i.item}</li>)}</ul>
        <h3 className="serif">Method</h3><ol>{recipe.steps.map((s, k) => <li key={k}>{s}</li>)}</ol>{recipe.notes.map((n, k) => <p key={k} className="lede">{n}</p>)}
        <div className="rate" role="group" aria-label="Rate this recipe">{[1, 2, 3, 4, 5].map(n => <button key={n} aria-label={`${n} stars`} className={(recipe.rating ?? 0) >= n ? "lit" : ""} onClick={() => rate(recipe, n)}>★</button>)}</div>
        <div className="row"><button className="ghost" disabled={recipe.cooked} onClick={() => rate(recipe, undefined, true)}>{recipe.cooked ? "Cooked ✓" : "I cooked this"}</button><button className="ghost" disabled={busy} onClick={() => go(true)}>Try another take</button></div></section>}
      {session && <section className="card"><p className="mono eyebrow">03 / More from the pantry</p><h2 className="serif">Keep cooking with SpazaChef</h2><label>PayFast receipt email<input type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" /></label>{checkoutErr && <p className="err" role="alert">{checkoutErr}</p>}<div className="row"><button type="button" className="ghost" disabled={checkoutBusy || !email.trim()} onClick={() => startCheckout("basic")}>{checkoutBusy ? "Opening checkout…" : "Basic · R15 · 30 recipes/day"}</button><button type="button" className="ghost" disabled={checkoutBusy || !email.trim()} onClick={() => startCheckout("premium")}>{checkoutBusy ? "Opening checkout…" : "Premium · R99 · 10,000 recipes/day"}</button></div></section>}
      <p className="mono eyebrow">Your kitchen memory</p>
      <div className="head"><h2 className="serif big">Recent recipes</h2>{recent.length > 3 && <button className="link" onClick={() => setAll(!all)}>{all ? "Show less" : "See all ›"}</button>}</div>
      {recent.length === 0 ? <div className="empty"><span aria-hidden>⟲</span><h3 className="serif">No recipes in the book yet.</h3><p>Your next good idea will show up here.</p></div>
        : shown.map(r => <button key={r.id} className="past" onClick={() => { setRecipe(r); scrollTo({ top: 0, behavior: "smooth" }); }}><b className="serif">{r.title}</b><span className="mono">{r.persona_name} · {r.minutes} min</span></button>)}
      </>}
    </main></>);
}

