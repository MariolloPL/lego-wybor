// Worker: serwuje stronę z public/ i trzyma wspólny postęp chłopców.
// Każdy kod rodzinny ma własny magazyn (Durable Object). Bez poprawnego kodu nie ma dostępu do danych.
import { DurableObject } from "cloudflare:workers";

const KEYS = new Set(["jas", "antek", "settings"]);
const ALPH = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";

function codeOk(c) {
  if (!/^[2-9A-HJKMNP-Z]{12}$/.test(c)) return false;
  let s = 0;
  for (let i = 0; i < 10; i++) s += (i + 1) * ALPH.indexOf(c[i]);
  return c[10] === ALPH[s % 31] && c[11] === ALPH[(s * 7 + 3) % 31];
}

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/api\/state\/([a-z]+)$/);
    if (!m) return env.ASSETS.fetch(request);
    const key = m[1];
    if (!KEYS.has(key)) return json({ error: "not_found" }, 404);

    const code = (request.headers.get("x-family-code") || "").toUpperCase().replace(/[^0-9A-Z]/g, "");
    if (!codeOk(code)) return json({ error: "auth" }, 401);
    const store = env.STORE.get(env.STORE.idFromName(code));

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
