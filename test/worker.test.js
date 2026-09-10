import test from "node:test";
import assert from "node:assert/strict";
import { githubJson, isValidDate } from "../src/worker.js";

test("accepts only real ISO calendar dates", () => {
  assert.equal(isValidDate("2026-09-10"), true);
  assert.equal(isValidDate("2026-02-29"), false);
  assert.equal(isValidDate("2026-9-10"), false);
});

test("decodes GitHub Contents API payload", async () => {
  const fetcher = async () => new Response(JSON.stringify({
    encoding: "base64", content: "eyJvayI6dHJ1ZX0=", sha: "abc123",
  }), { status: 200 });
  const result = await githubJson("taifex", "2026-09-10", {}, fetcher);
  assert.deepEqual(result, { data: { ok: true }, sha: "abc123" });
});

test("maps an absent GitHub file to missing", async () => {
  const result = await githubJson("twse", "2026-09-10", {}, async () => new Response(null, { status: 404 }));
  assert.deepEqual(result, { missing: true });
});
