// Worker: serwuje stronę z public/ i trzyma wspólny postęp chłopców (Durable Object).
// Dostęp do danych tylko z kodem rodzinnym równym sekretowi FAMILY_CODE ustawionemu w Cloudflare
// (Settings → Variables and Secrets). Kodu nie ma w repozytorium.
import { DurableObject } from "cloudflare:workers";

const KEYS = new Set(["jas", "antek", "settings"]);
const norm = (x) => String(x || "").toUpperCase().replace(/[^0-9A-Z]/g, "");

// porównanie w stałym czasie, żeby nie zdradzać długości zgodnego fragmentu
function sameCode(a, b) {
  if (!a || !b) return false;
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    // diagnostyka: czy sekret jest ustawiony (bez ujawniania wartości)
    if (url.pathname === "/api/health") return json({ ok: true, familyCodeSet: !!norm(env.FAMILY_CODE) });
    const m = url.pathname.match(/^\/api\/state\/([a-z]+)$/);
    if (!m) return env.ASSETS.fetch(request);
    const key = m[1];
    if (!KEYS.has(key)) return json({ error: "not_found" }, 404);

    if (!sameCode(norm(request.headers.get("x-family-code")), norm(env.FAMILY_CODE))) return json({ error: "auth" }, 401);
    const store = env.STORE.get(env.STORE.idFromName("family"));

    if (request.method === "GET") {
      const rec = await store.read(key);
      return rec ? json(rec) : json({ error: "empty" }, 404);
    }
    if (request.method === "PUT") {
      const text = await request.text();
      if (text.length > 250_000) return json({ error: "too_big" }, 413);
      let data;
      try { data = JSON.parse(text); } catch { return json({ error: "bad_json" }, 400); }
      if (!data || typeof data !== "object" || Array.isArray(data)) return json({ error: "bad_body" }, 400);
      const version = await store.write(key, data);
      return json({ version });
    }
    return json({ error: "method" }, 405);
  },
};

export class FamilyStore extends DurableObject {
  async read(key) {
    return (await this.ctx.storage.get(key)) ?? null;
  }
  async write(key, data) {
    const cur = await this.ctx.storage.get(key);
    const version = (cur?.version || 0) + 1;
    await this.ctx.storage.put(key, { version, data, updatedAt: new Date().toISOString() });
    return version;
  }
}
