import { useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL ?? "";
const PERSONAS = [
  { id: "zanele", ini: "AZ", name: "Auntie Zanele", tag: "Comfort food, big flavour", bio: "Generous, warm, and deeply practical. She knows how to stretch a pantry." },
  { id: "jabu", ini: "BJ", name: "Braai Boss Jabu", tag: "Fire, smoke, and confidence", bio: "Bold and direct, with a soft spot for clever shortcuts and a good char." },
  { id: "farah", ini: "CF", name: "Chef Farah", tag: "Spice with a story", bio: "Bright, aromatic, and precise, bringing Cape Malay warmth to every pot." },
  { id: "raj", ini: "RN", name: "Raj from next door", tag: "Clever swaps, no fuss", bio: "Playful and resourceful, turning everyday ingredients into something worth sharing." },
];
type Recipe = { id: string; title: string; persona_name: string; intro: string; serves: number; minutes: number; ingredients: { item: string; amount: string }[]; steps: string[]; notes: string[]; rating?: number | null; cooked?: boolean };
const uid = (): Record<string, string> => { const t = localStorage.getItem("token"); return t ? { Authorization: `Bearer ${t}` } : {}; };
async function api<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(API + path, { method: body ? "POST" : "GET", headers: { "Content-Type": "application/json", ...uid() }, body: body ? JSON.stringify(body) : undefined });
  const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(typeof j.detail === "string" ? j.detail : "Something went wrong. Try again.");
  return j;
}
export default function App() {
  const [persona, setPersona] = useState("zanele"), [ing, setIng] = useState(""), [diet, setDiet] = useState(""), [serves, setServes] = useState(4), [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false), [err, setErr] = useState(""), [recipe, setRecipe] = useState<Recipe | null>(null), [recent, setRecent] = useState<Recipe[]>([]), [all, setAll] = useState(false);
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => { const f = () => setOnline(navigator.onLine); addEventListener("online", f); addEventListener("offline", f); return () => { removeEventListener("online", f); removeEventListener("offline", f); }; }, []);
  useEffect(() => { api<Recipe[]>("/api/recipes").then(r => { setRecent(r); localStorage.setItem("recent", JSON.stringify(r)); }).catch(() => setRecent(JSON.parse(localStorage.getItem("recent") || "[]"))); }, []);
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
      <p className="mono eyebrow">Your kitchen memory</p>
      <div className="head"><h2 className="serif big">Recent recipes</h2>{recent.length > 3 && <button className="link" onClick={() => setAll(!all)}>{all ? "Show less" : "See all ›"}</button>}</div>
      {recent.length === 0 ? <div className="empty"><span aria-hidden>⟲</span><h3 className="serif">No recipes in the book yet.</h3><p>Your next good idea will show up here.</p></div>
        : shown.map(r => <button key={r.id} className="past" onClick={() => { setRecipe(r); scrollTo({ top: 0, behavior: "smooth" }); }}><b className="serif">{r.title}</b><span className="mono">{r.persona_name} · {r.minutes} min</span></button>)}
    </main></>);
}
