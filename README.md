# Qwen Expression Pack Generator

Standalone **expression-pack** service + SillyTavern extension.

- **Backend**: containerized FastAPI/Gradio — deploy on any Dockhand/Hawser node
- **Frontend**: pure ST extension, installable by **Git URL**
- Reachable over **Tailscale / Docktail** (no localhost coupling to ST)

Powered by [`jblast94/Qwen-Image-Edit-NSFW`](https://huggingface.co/spaces/jblast94/Qwen-Image-Edit-NSFW).

---

## 1. Deploy the service (any node)

On the machine that should run the generator (`ai1` or a worker):

```bash
git clone https://github.com/Jblast94/qwen-expression-pack-generator.git
cd qwen-expression-pack-generator

export HF_TOKEN=hf_xxxxxxxx   # optional, recommended

# Standalone stack — does NOT touch SillyTavern
docker compose -f docker-compose.service.yml up -d --build
```

Or import `docker-compose.service.yml` as a stack in **Dockhand** on `ai1` and let Hawser deploy it.

Listens on **7865**. Docktail labels are included:

```yaml
docktail.service.enable=true
docktail.service.name=expression-pack
docktail.service.port=7865
```

---

## 2. Install the SillyTavern extension (Git URL)

In SillyTavern:

**Extensions → Install Extension → Git URL**

```
https://github.com/Jblast94/qwen-expression-pack-generator
```

**Branch: `extension`**

That branch has `manifest.json`, `index.js`, and `style.css` at the **repo root**, so ST installs it like any other third-party extension.

---

## 3. Point the extension at the service

The extension runs **in the browser**. Set **Backend URL** to whatever reaches the container from that browser:

| From | Backend URL |
|------|-------------|
| Same machine as the container | `http://localhost:7865` |
| Another node on Tailscale | `http://<magicdns-or-tailnet-ip>:7865` |
| Via Docktail | `https://expression-pack.<your-docktail-host>` |

Do **not** use `http://expression-pack:7865` — that name only exists on the Docker network, not in the browser.

---

## API (agents / n8n)

```bash
curl -X POST http://<host>:7865/api/generate \
  -F "file=@reference.png" \
  -F "preset=full_pack" \
  -F "character_name=Missy" \
  -F "steps=4"
```

Presets: `standard_28` | `nsfw_extra` | `full_pack`

---

## Repo layout

```
main branch
├── app.py, qwen_client.py, expressions.py, packager.py
├── Dockerfile
├── docker-compose.service.yml   ← use this (standalone)
├── docker-compose.yml           ← optional example only
└── extension/ / st-extension/    ← extension source

extension branch
├── manifest.json, index.js, style.css   ← at root for ST Git install
```

---

## License

MIT
