# Master Pipeline Plan — Character Sprites, Grok Imagine & Eliza Swarm

**Status:** Draft v1.1 (2026-08-31)  
**Owner:** Jblast94  
**Repos involved:** `qwen-expression-pack-generator`, `xcreator-pipeline`  
**Goal:** One modular, cheap, expandable pipeline that turns a single reference image + trend data into persistent characters, expression packs, social posts, and monetized content — without a monolith.

---

## 1. Core Principles (non-negotiable)

- **Small pieces, each replaceable.** No god containers. No giant codebases.
- **Shared state, not shared process.** Postgres (pgvector) + MinIO + Valkey are the only shared layers.
- **Generators are swappable.** Imagine first, Qwen fallback, HF Spaces as CPU workers.
- **Memory compounds.** Every decision, prompt, asset, and result is stored. Nothing evaporates between sessions.
- **Agents are a crew, not scripts.** Persistent characters with roles, history, and handoffs.
- **Slow and simple first.** Prove each piece works before adding the next layer.

---

## 2. Architecture Overview

```
[Trend / Affiliate Scraper] 
        ↓
[Scoring Worker (HF CPU Space / Dagger)] 
        ↓
[Eliza Agents (persistent crew)] ↔ [Valkey cache + rate limits]
        ↓
[Image Router]
   ├── Grok Imagine (fast, safe, cheap) → primary
   └── Qwen-Image-Edit-NSFW (HF Space) → fallback (RunPod deferred)
        ↓
[Asset Store] — local gallery folder first → MinIO + Postgres/pgvector later
        ↓
[Gallery / Export] — simple folder + optional ZIP (Immich later)
        ↓
[Posting] — X (3 accounts) + Reddit via Eliza + Playwright
        ↓
[Performance loop] → back into scoring + memory
```

---

## 3. The Sprite Project (current seed)

**Repo:** `Jblast94/qwen-expression-pack-generator`  
**What it does today:** Takes one reference image → generates expression set via `jblast94/Qwen-Image-Edit-NSFW` HF Space → packages into SillyTavern ZIP + Lumiverse CHARX.

**Known issues to fix:**
- RunPod worker returns the *same* image (no actual edit). **Deferred** — do not spend money on it during development.
- Qwen space errors intermittently from the worker even though the space works fine in-account.
- Output is hard-wired to SillyTavern; needs gallery + ZIP-first path.

**Immediate upgrades (keep it simple):**
1. Add `gallery` output mode (write to a simple folder or later MinIO + Postgres row, skip ST packaging by default).
2. Add `imagine` backend toggle (call Grok Imagine API when safe; fall back to Qwen).
3. Fix Qwen error handling: better surfacing + retry with jitter.
4. Keep ST/Lumiverse as *optional export*, not the default.
5. Expose clean `/api/generate` for n8n + Dagger + Eliza to call.
6. Orchestrate generation through Hugging Face Gradio Spaces in plain Python.

---

## 4. Grok Imagine Integration

- **Model:** `grok-imagine-image-2.0` (Quality Mode on grok.com/imagine).
- **Cost:** ~4–6¢ per 1K image, ~8¢ at 2K. Smart resize for 16:9 / 9:16 / 1:1.
- **Routing rule:** If prompt is safe → Imagine. If moderated/filtered/NSFW → queue to Qwen space fallback.
- **Three X accounts** = three API keys = three rate pools. Fan out the same trend across accounts.
- **No RunPod** until explicitly re-enabled.

---

## 5. Eliza Crew (persistent agents)

**Repo:** `Jblast94/xcreator-pipeline` (existing characters + bridge).

- Characters live in `agents/characters/*.json` with persistent memory in Postgres.
- Each has a role: trend scanner, copywriter, image director, poster, analyst.
- They pull from the shared gallery for visual context.
- Memory layer: decisions, what worked, what failed — survives between sessions.
- Old RuCode-style task structure (clear roles, explicit handoffs) is the template.

---

## 6. Storage & Database Consolidation

**Problem:** Databases scattered everywhere, unshared.

**Target (later):**
- **One Postgres + pgvector** (Neon or Supabase) for: products, posts, assets, performance, agent memory, embeddings.
- **MinIO** (S3-compatible) for raw images + vectors on separate volumes.
- **Valkey** for rate limits, cache, queues only — never vectors.
- Homelab cleanup: pick the worst directory, move into clean structure, one at a time.

**Now:** Prove the connector with one table before migrating everything.

---

## 7. Orchestration

- **Dagger** for pipeline steps (plain Python, cached, no god containers).
- **n8n** (Docker, upgraded) as the workflow glue + AI sandbox on HF CPU Spaces.
- **HF CPU Spaces** as cheap burst workers (2 vCPU / 16 GB free tier, multiple Spaces).
- **RunPod Flash** — deferred. Not used during development.

---

## 8. Monetization Loop

1. Scrape trending products + affiliate offers.
2. Score by margin + conversion history.
3. Feed winners to Eliza agents.
4. Agents write post + attach Imagine/Qwen image.
5. Post to X + Reddit.
6. Track clicks/sales → write back to Postgres → scoring improves.

Start with **one category, one program, one account**. Close the loop end-to-end before scaling.

---

## 9. Multi-Agent Expert Team (assigned roles)

| Agent | Role | First task |
|-------|------|------------|
| **Architect** | Owns this plan, keeps pieces modular | Review + approve this doc |
| **Sprite Engineer** | Fixes qwen-expression-pack-generator | Gallery mode + Imagine toggle (no RunPod) |
| **Imagine Router** | Builds Grok Imagine client + fallback logic | Endpoint + moderation handoff |
| **Eliza Keeper** | Maintains persistent characters + memory | Re-point old characters at new Postgres/Valkey |
| **Storage Consolidator** | One Postgres + MinIO + Valkey | Schema + migration plan (Neon/Supabase) |
| **Orchestrator** | Dagger + n8n + HF Spaces glue | First simple end-to-end Dagger pipeline |
| **Monetization Scout** | Scraping + scoring + affiliate | One category MVP |
| **Gallery Curator** | Simple gallery + ZIP export | Live folder + nightly archive (Immich later) |
| **QA / Tester** | Runs the loop, logs failures | Daily smoke test of sprite + Imagine path |

Each agent gets a short brief, a single repo or service to own, and a clear handoff contract. No agent touches another agent's code without a PR.

---

## 10. Phased Rollout

**Phase 0 — Now (this session)**
- This plan committed to repo.
- Issues created for each agent's first task.
- RunPod deferred.

**Phase 1 — Sprite hardening (1–2 days)**
- Gallery output, Imagine toggle, Qwen error handling.
- Test: one reference image → gallery folder, no ST required.
- First simple Dagger pipeline.

**Phase 2 — Storage consolidation (2–3 days)**
- Single Postgres schema (Neon/Supabase), MinIO buckets, Valkey only for cache.
- Migrate existing scattered DBs one at a time.

**Phase 3 — Eliza revival (3–5 days)**
- Re-point characters, add memory, connect to gallery.
- First autonomous post with generated sprite.

**Phase 4 — Monetization MVP (1 week)**
- One category, one affiliate program, one account.
- Closed loop: scrape → score → generate → post → track.

**Phase 5 — Scale**
- Add accounts, categories, more HF Spaces, more Eliza characters.
- The platform gets wider, not taller.

---

## 11. Success Metrics

- Time from reference image to posted asset: < 5 min.
- Cost per generated asset: < $0.10.
- Zero single points of failure (kill any one service, pipeline still runs).
- Every asset has a Postgres row + MinIO object + embedding.
- Agent memory grows week over week (measurable: fewer repeated mistakes).

---

*This is a living document. Update it as the crew ships.*
