const URL = import.meta.env.VITE_SUPABASE_URL as string;
const KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string;
export type Session = { access_token: string; refresh_token: string; email: string; expires_at: number };
export const getSession = (): Session | null => {
  try { return JSON.parse(localStorage.getItem("session") || "null"); } catch { return null; }
};
const save = (s: Session | null) => (s ? localStorage.setItem("session", JSON.stringify(s)) : localStorage.removeItem("session"));
async function call(path: string, body: unknown) {
  const r = await fetch(`${URL}/auth/v1/${path}`, { method: "POST", headers: { apikey: KEY, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.msg || j.error_description || "Sign-in failed. Check your details and try again.");
  return j;
}
const toSession = (j: any): Session => ({ access_token: j.access_token, refresh_token: j.refresh_token, email: j.user?.email ?? "", expires_at: Date.now() / 1000 + j.expires_in });
export async function signIn(email: string, password: string) { const s = toSession(await call("token?grant_type=password", { email, password })); save(s); return s; }
export async function signUp(email: string, password: string) {
  const j = await call("signup", { email, password });
  if (j.access_token) { const s = toSession(j); save(s); return s; }
  return null; // email confirmation required
}
export const signOut = () => save(null);
export async function authHeader(): Promise<Record<string, string>> {
  let s = getSession(); if (!s) return {};
  if (s.expires_at - 60 < Date.now() / 1000) {
    try { s = toSession(await call("token?grant_type=refresh_token", { refresh_token: s.refresh_token })); save(s); }
    catch { save(null); return {}; }
  }
  return { Authorization: `Bearer ${s.access_token}` };
}
