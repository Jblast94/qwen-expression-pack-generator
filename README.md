# Qwen Expression Pack Generator

Expression Pack Generator for **SillyTavern** + **Lumiverse**, powered by [`jblast94/Qwen-Image-Edit-NSFW`](https://huggingface.co/spaces/jblast94/Qwen-Image-Edit-NSFW).

Fully containerized so it is reachable from Docker, your browser, and Tailnet / Docktail.

## Repository Structure

```
├── app.py
├── qwen_client.py
├── expressions.py
├── packager.py
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml          # Full stack: SillyTavern + expression-pack
├── README.md
└── st-extension/               # Drop into ST third-party extensions
    ├── index.js
    ├── manifest.json
    └── style.css
```

## Recommended: Docker Compose (with your SillyTavern)

1. Place this repo next to (or copy the files into) your existing ST compose directory, **or** merge the `expression-pack` service from `docker-compose.yml` into your current compose.

2. Make sure the ST extension is available:

```bash
# Copy extension into the folder that is mounted as third-party extensions
cp -r st-extension ./extensions/st-expression-pack-extension
```

3. Start the stack:

```bash
export HF_TOKEN=hf_xxxxxxxx   # optional but recommended
docker compose up -d --build
```

4. Open SillyTavern → Extensions → **Qwen Expression Pack**

5. Set **Backend URL** to one of:
   - `http://localhost:7865`          (same machine browser)
   - `http://<your-tailnet-ip>:7865`  (other devices on Tailnet)
   - your Docktail URL for `expression-pack`

6. Select a character with an avatar → **Generate Expression Pack**

### Why not `http://expression-pack:7865`?

The extension runs **in the browser**, not inside the SillyTavern container.  
`expression-pack` is only resolvable on the Docker network. The browser needs a host-reachable address (published port 7865 or Docktail).

## Standalone (no ST in the same compose)

```bash
docker build -t expression-pack .
docker run -d --name expression-pack \
  -p 7865:7865 \
  -e HF_TOKEN=hf_xxxxxxxx \
  -v expression-pack-data:/tmp/expression_packs \
  expression-pack
```

## Local (uv, no Docker)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
export HF_TOKEN=hf_xxxxxxxx
uv run python app.py
# → http://localhost:7865
```

## API

```bash
curl -X POST http://localhost:7865/api/generate \
  -F "file=@reference.png" \
  -F "preset=full_pack" \
  -F "character_name=Missy" \
  -F "steps=4"
```

## Presets

- `standard_28` – classic SillyTavern / Lumiverse emotions  
- `nsfw_extra` – flirty, seductive, lustful, soft ahegao, afterglow, etc.  
- `full_pack` – both (recommended)

## License

MIT
