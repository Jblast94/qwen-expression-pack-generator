# Qwen Expression Pack Generator

Expression Pack Generator for **SillyTavern** + **Lumiverse**, powered by your Hugging Face space [`jblast94/Qwen-Image-Edit-NSFW`](https://huggingface.co/spaces/jblast94/Qwen-Image-Edit-NSFW).

## Repository Structure

```
├── app.py                 # FastAPI + Gradio backend
├── qwen_client.py         # Gradio queue client for the HF space
├── expressions.py         # Expression presets (standard 28 + NSFW)
├── packager.py            # SillyTavern ZIP + Lumiverse CHARX builders
├── requirements.txt
├── README.md
└── st-extension/          # SillyTavern extension
    ├── index.js
    ├── manifest.json
    └── style.css
```

## Quick Start – Backend

```bash
pip install -r requirements.txt
export HF_TOKEN=hf_xxxxxxxx   # optional but recommended
python app.py
# → http://localhost:7865
```

## Quick Start – SillyTavern Extension

1. Copy the entire `st-extension/` folder into:
   `SillyTavern/public/scripts/extensions/third-party/st-expression-pack-extension/`
2. Restart SillyTavern or enable the extension in the Extensions panel
3. Select a character that has an avatar
4. Open **Extensions** settings → **Qwen Expression Pack**
5. Click **Generate Expression Pack for Current Character**
6. The ZIP downloads automatically → use **Upload sprite pack (ZIP)** in Character Expressions

## API

```bash
curl -X POST http://localhost:7865/api/generate \\
  -F "file=@reference.png" \\
  -F "preset=full_pack" \\
  -F "character_name=Missy" \\
  -F "steps=4"
```

Returns download URLs for both the SillyTavern ZIP and Lumiverse CHARX.

## Presets

- `standard_28` – classic SillyTavern / Lumiverse emotions
- `nsfw_extra` – flirty, seductive, lustful, soft ahegao, afterglow, etc.
- `full_pack` – both (recommended)

## License

MIT
