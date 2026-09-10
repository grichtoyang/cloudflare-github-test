const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const SOURCES = new Set(["taifex", "twse"]);

function json(body, init = {}) {
  const headers = new Headers(init.headers);
  headers.set("content-type", "application/json; charset=utf-8");
  headers.set("x-content-type-options", "nosniff");
  return new Response(JSON.stringify(body), { ...init, headers });
}

function error(status, code, message, requestId, details) {
  return json(
    { ok: false, error: { code, message, ...(details ? { details } : {}) }, request_id: requestId },
    { status },
  );
}

function requestId(request) {
  return request.headers.get("cf-ray") || crypto.randomUUID();
}

function corsHeaders(request, env) {
  const origin = request.headers.get("origin");
  const origins = (env.ALLOWED_ORIGINS || "").split(",").map((item) => item.trim()).filter(Boolean);
  if (!origin || !origins.includes(origin)) return {};
  return {
    "access-control-allow-origin": origin,
    "access-control-allow-methods": "GET, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    vary: "Origin",
  };
}

function isValidDate(value) {
  if (!DATE_PATTERN.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00.000Z`);
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

function cacheTtl(env) {
  const ttl = Number(env.CACHE_TTL_SECONDS ?? 300);
  return Number.isFinite(ttl) ? Math.min(Math.max(ttl, 0), 86400) : 300;
}

async function githubJson(source, date, env, fetcher) {
  const owner = env.GITHUB_OWNER || "grichtoyang";
  const repo = env.GITHUB_REPO || "cloudflare-github-test";
  const branch = env.GITHUB_BRANCH || "main";
  const path = `data/${source}/${date}.json`;
  const headers = { accept: "application/vnd.github+json", "user-agent": "market-data-github-bridge" };
  if (env.GITHUB_TOKEN) headers.authorization = `Bearer ${env.GITHUB_TOKEN}`;

  const response = await fetcher(
    `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/contents/${path}?ref=${encodeURIComponent(branch)}`,
    { headers },
  );
  if (response.status === 404) return { missing: true };
  if (!response.ok) throw new Error(`GitHub returned ${response.status}`);

  const file = await response.json();
  if (file.encoding !== "base64" || typeof file.content !== "string") throw new Error("GitHub returned an unsupported file payload");
  const bytes = Uint8Array.from(atob(file.content.replace(/\n/g, "")), (char) => char.charCodeAt(0));
  return { data: JSON.parse(new TextDecoder().decode(bytes)), sha: file.sha };
}

async function readData(source, date, env, context, fetcher = fetch) {
  const cacheKey = new Request(`https://cache.internal/v1/data/${source}/${date}`);
  const cache = caches.default;
  const cached = await cache.match(cacheKey);
  if (cached) return { response: cached, cache: "HIT" };

  const result = await githubJson(source, date, env, fetcher);
  if (result.missing) return { missing: true };
  const response = json({ ok: true, source: source.toUpperCase(), date, data: result.data, github_sha: result.sha }, {
    headers: { "cache-control": `public, max-age=${cacheTtl(env)}` },
  });
  if (cacheTtl(env) > 0) context.waitUntil(cache.put(cacheKey, response.clone()));
  return { response, cache: "MISS" };
}

function withCommonHeaders(response, cors, cache, id) {
  const headers = new Headers(response.headers);
  headers.set("x-request-id", id);
  if (cache) headers.set("x-cache", cache);
  for (const [key, value] of Object.entries(cors)) headers.set(key, value);
  return new Response(response.body, { status: response.status, headers });
}

export default {
  async fetch(request, env, context) {
    const id = requestId(request);
    const cors = corsHeaders(request, env);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method !== "GET") return withCommonHeaders(error(405, "method_not_allowed", "Only GET and OPTIONS are supported.", id), cors, null, id);

    const { pathname } = new URL(request.url);
    if (pathname === "/health") return withCommonHeaders(json({ ok: true, service: "market-data-github-bridge", version: "1.0.0" }), cors, null, id);

    const dataMatch = pathname.match(/^\/v1\/data\/(taifex|twse)\/(.+)$/);
    if (dataMatch) {
      const [, source, date] = dataMatch;
      if (!isValidDate(date)) return withCommonHeaders(error(400, "invalid_date", "Date must be a real calendar date in YYYY-MM-DD format.", id), cors, null, id);
      try {
        const result = await readData(source, date, env, context);
        if (result.missing) return withCommonHeaders(error(404, "not_found", "No data file exists for this source and date.", id), cors, null, id);
        return withCommonHeaders(result.response, cors, result.cache, id);
      } catch (cause) {
        console.error({ request_id: id, source, date, cause: String(cause) });
        return withCommonHeaders(error(502, "github_unavailable", "Unable to retrieve data from GitHub.", id), cors, null, id);
      }
    }
    return withCommonHeaders(error(404, "not_found", "Route not found.", id), cors, null, id);
  },
};

export { isValidDate, githubJson };
