# Market Data GitHub Bridge

Production Cloudflare Worker that exposes the repository's daily TAIFEX and TWSE JSON files through a stable, validated API. It uses the GitHub Contents API rather than a hard-coded raw URL, so the same worker works with public repositories and private repositories when given a read-only token.

## API

| Route | Result |
| --- | --- |
| `GET /health` | Worker health and version |
| `GET /v1/data/taifex/YYYY-MM-DD` | TAIFEX daily JSON |
| `GET /v1/data/twse/YYYY-MM-DD` | TWSE daily JSON |

Every successful data response is wrapped as `{ ok, source, date, data, github_sha }`. Errors use `{ ok: false, error: { code, message }, request_id }`. Invalid dates, unsupported methods and missing files return `400`, `405` and `404`; GitHub failures return `502`.

## Deploy

```bash
npm install
npx wrangler deploy
```

For a private repository, create a GitHub fine-grained token with **Contents: Read-only**, then store it without committing it:

```bash
npx wrangler secret put GITHUB_TOKEN
```

Set `ALLOWED_ORIGINS` in `wrangler.toml` to the exact production web origins that may call the API. The worker caches successful GitHub responses with Cloudflare's Cache API for 300 seconds by default; tune `CACHE_TTL_SECONDS` as needed.

## Verify

```bash
npm test
npx wrangler dev
curl http://localhost:8787/health
curl http://localhost:8787/v1/data/taifex/2026-09-10
```

No write token is required for this bridge. Data publishing remains a separate GitHub workflow, which keeps the public API read-only and limits blast radius.
