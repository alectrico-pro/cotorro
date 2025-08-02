import logging
from workers import Response
from urllib.parse import urlparse, parse_qs
import json
from js import console

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_fetch(request, env):
    url = urlparse(request.url)
    params = parse_qs(url.query)

    console.log(f"Handling request {url.path} with params {params}")

    if url.path == "/":
        msg = env.GREETING
        return Response(msg)

    if url.path == "/cache":
        # use KV
        key = params.get("key", ["default"])[0]
        cached = await env.MY_CACHE.get(key)
        if cached:
            return Response(f"From KV: {cached}")

        # fallback compute
        value = f"computed‑{key}"
        await env.MY_CACHE.put(key, value)
        return Response(f"Stored & returned {value}")

    if url.path.startswith("/proxy"):
        body = await request.json()
        # Proxy to external API
        upstream = f"{env.API_URL}/users/{body.get('id')}"
        js_resp = await request.fetch(upstream)
        return Response.make(js_resp.body, status=js_resp.status, headers=dict(js_resp.headers))

    return Response("Not Found", status=404)
