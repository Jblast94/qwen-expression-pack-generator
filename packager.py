"""
Creates ready-to-import packages for SillyTavern and Lumiverse.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Dict, Optional

from PIL import Image


def _ensure_png(image_bytes: bytes) -> bytes:
    """Convert any image to PNG bytes."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def create_sillytavern_zip(
    expressions: Dict[str, bytes],
    character_name: str = "character",
) -> bytes:
    """
    Build a ZIP that SillyTavern can import via
    "Upload sprite pack (ZIP)".

    Files are named exactly as ST expects:
        joy.png, sadness.png, etc.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in expressions.items():
            if not data:
                continue
            png = _ensure_png(data)
            # ST is case-sensitive on some systems; keep lowercase
            zf.writestr(f"{name.lower()}.png", png)
    buf.seek(0)
    return buf.read()


def create_lumiverse_charx(
    expressions: Dict[str, bytes],
    character_name: str = "character",
    card_json: Optional[dict] = None,
) -> bytes:
    """
    Build a minimal CHARX (ZIP) that Lumiverse can import.

    Structure:
        card.json          (optional, minimal if not provided)
        avatar.png         (first expression or neutral)
        expressions/
            joy.png
            ...
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # expressions folder
        for name, data in expressions.items():
            if not data:
                continue
            png = _ensure_png(data)
            zf.writestr(f"expressions/{name.lower()}.png", png)

        # avatar = neutral or first available
        avatar_key = "neutral" if "neutral" in expressions else next(iter(expressions), None)
        if avatar_key and expressions.get(avatar_key):
            zf.writestr("avatar.png", _ensure_png(expressions[avatar_key]))

        # minimal card if none supplied
        if card_json is None:
            card_json = {
                "name": character_name,
                "description": f"Generated expression pack for {character_name}",
                "personality": "",
                "scenario": "",
                "first_mes": "",
                "mes_example": "",
                "creator_notes": "Expression pack generated with Qwen-Image-Edit-NSFW",
                "tags": ["expression-pack", "qwen-edit"],
                "extensions": {
                    "lumiverse": {
                        "expressions": {k: f"expressions/{k.lower()}.png" for k in expressions}
                    }
                },
            }
        zf.writestr("card.json", json.dumps(card_json, indent=2))

    buf.seek(0)
    return buf.read()


def create_both_packs(
    expressions: Dict[str, bytes],
    character_name: str = "character",
) -> Dict[str, bytes]:
    """Return both formats."""
    return {
        "sillytavern.zip": create_sillytavern_zip(expressions, character_name),
        "lumiverse.charx": create_lumiverse_charx(expressions, character_name),
    }
