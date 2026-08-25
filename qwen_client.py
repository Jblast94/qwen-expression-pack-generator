"""
Client for jblast94/Qwen-Image-Edit-NSFW Gradio space.
Handles the full Gradio queue protocol (upload → join → stream).
"""

from __future__ import annotations

import asyncio
import io
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("qwen_client")

SPACE_URL = "https://jblast94-qwen-image-edit-nsfw.hf.space"
API_PREFIX = f"{SPACE_URL}/gradio_api"


class QwenImageEditClient:
    def __init__(
        self,
        hf_token: Optional[str] = None,
        timeout: float = 180.0,
        space_url: str = SPACE_URL,
    ):
        self.space_url = space_url.rstrip("/")
        self.api_prefix = f"{self.space_url}/gradio_api"
        self.timeout = timeout
        headers = {}
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=30.0),
            headers=headers,
            follow_redirects=True,
        )

    async def close(self):
        await self.client.aclose()

    async def _upload_file(self, image_bytes: bytes, filename: str = "ref.png") -> Dict[str, Any]:
        """Upload image and return Gradio FileData dict."""
        files = {"files": (filename, image_bytes, "image/png")}
        resp = await self.client.post(f"{self.api_prefix}/upload", files=files)
        resp.raise_for_status()
        data = resp.json()
        # Gradio returns a list of paths
        if isinstance(data, list) and len(data) > 0:
            path = data[0]
        else:
            path = data
        return {
            "path": path,
            "url": None,
            "size": len(image_bytes),
            "orig_name": filename,
            "mime_type": "image/png",
            "is_stream": False,
            "meta": {"_type": "gradio.FileData"},
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def edit(
        self,
        image_bytes: bytes,
        prompt: str,
        negative_prompt: str = "",
        seed: int = 0,
        randomize_seed: bool = True,
        true_guidance_scale: float = 1.0,
        num_inference_steps: int = 4,
        height: int = 0,          # 0 = keep original
        width: int = 0,
        rewrite_prompt: bool = False,
        filename: str = "ref.png",
    ) -> Tuple[bytes, int]:
        """
        Run one edit job.
        Returns (result_image_bytes, used_seed)
        """
        session_hash = str(uuid.uuid4())

        # 1. Upload
        file_data = await self._upload_file(image_bytes, filename)

        # 2. Build payload for /infer
        # Order matches the API schema we extracted
        payload = {
            "data": [
                [file_data],                          # images
                prompt,                               # prompt
                negative_prompt,                      # negative_prompt
                seed,                                 # seed
                randomize_seed,                       # randomize_seed
                true_guidance_scale,                  # true_guidance_scale
                num_inference_steps,                  # num_inference_steps
                height if height > 0 else 256,        # height (space default)
                width if width > 0 else 256,          # width
                rewrite_prompt,                       # rewrite_prompt
                0,                                    # zerogpu_budget
            ],
            "fn_index": 0,          # /infer is usually the first public endpoint
            "session_hash": session_hash,
            "trigger_id": 0,
        }

        # 3. Join queue
        join_resp = await self.client.post(
            f"{self.api_prefix}/queue/join",
            json=payload,
        )
        join_resp.raise_for_status()
        join_data = join_resp.json()
        event_id = join_data.get("event_id")

        # 4. Stream results
        result_image: Optional[bytes] = None
        used_seed: int = seed

        async with self.client.stream(
            "GET",
            f"{self.api_prefix}/queue/data",
            params={"session_hash": session_hash},
        ) as stream:
            async for line in stream.aiter_lines():
                if not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                if not raw:
                    continue
                try:
                    import json
                    msg = json.loads(raw)
                except Exception:
                    continue

                msg_type = msg.get("msg")
                if msg_type == "process_completed":
                    output = msg.get("output", {})
                    data = output.get("data", [])
                    if data and len(data) >= 1:
                        gallery = data[0]
                        # gallery is usually a list of FileData-like objects
                        if isinstance(gallery, list) and len(gallery) > 0:
                            item = gallery[0]
                            if isinstance(item, dict):
                                # Can be {"image": {...}} or direct FileData
                                img_info = item.get("image") or item
                                url = img_info.get("url")
                                path = img_info.get("path")
                                if url:
                                    # download
                                    img_resp = await self.client.get(url)
                                    img_resp.raise_for_status()
                                    result_image = img_resp.content
                                elif path:
                                    # path may be relative
                                    full = f"{self.space_url}/file={path}" if not path.startswith("http") else path
                                    img_resp = await self.client.get(full)
                                    img_resp.raise_for_status()
                                    result_image = img_resp.content
                        if len(data) >= 2:
                            used_seed = data[1] or seed
                    break
                elif msg_type == "process_starts":
                    logger.info("Job started on ZeroGPU...")
                elif msg_type == "estimation":
                    rank = msg.get("rank", "?")
                    logger.info(f"Queue rank: {rank}")
                elif msg_type == "error":
                    raise RuntimeError(f"Space error: {msg}")

        if result_image is None:
            raise RuntimeError("No image returned from Qwen space")

        return result_image, used_seed

    async def generate_pack(
        self,
        reference_bytes: bytes,
        expressions: Dict[str, str],
        steps: int = 4,
        guidance: float = 1.0,
        negative: str = "blurry, low quality, deformed, extra limbs, watermark, text",
        max_concurrent: int = 2,
    ) -> Dict[str, bytes]:
        """
        Generate a full expression pack.
        Returns {expression_name: image_bytes}
        """
        results: Dict[str, bytes] = {}
        sem = asyncio.Semaphore(max_concurrent)

        async def _one(name: str, prompt: str):
            async with sem:
                logger.info(f"Generating: {name}")
                try:
                    img, _ = await self.edit(
                        image_bytes=reference_bytes,
                        prompt=prompt,
                        negative_prompt=negative,
                        num_inference_steps=steps,
                        true_guidance_scale=guidance,
                        randomize_seed=True,
                    )
                    results[name] = img
                    logger.info(f"✓ {name}")
                except Exception as e:
                    logger.error(f"✗ {name}: {e}")
                    results[name] = b""  # placeholder so pack still builds

        tasks = [_one(name, prompt) for name, prompt in expressions.items()]
        await asyncio.gather(*tasks)
        return results
