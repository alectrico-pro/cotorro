import logging
from workers import Response
from urllib.parse import urlparse, parse_qs
import json
from js import console

import uuid
#import requests
#from dotenv import load_dotenv #no lo acepta cloudflare


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




def create_flow():
    flow_base_url = (
        f"https://graph.facebook.com/v18.0/{WHATSAPP_BUSINESS_ACCOUNT_ID}/flows"
    )
    flow_creation_payload = {"name": "<FLOW-NAME>", "categories": '["SURVEY"]'}
    flow_create_response = requests.request(
        "POST", flow_base_url, headers=auth_header, data=flow_creation_payload
    )

    try:
        global created_flow_id
        created_flow_id = flow_create_response.json()["id"]
        graph_assets_url = f"https://graph.facebook.com/v18.0/{created_flow_id}/assets"

        upload_flow_json(graph_assets_url)
        publish_flow(created_flow_id)

        print("FLOW CREATED!")
        return make_response("FLOW CREATED", 200)
    except:
        return make_response("ERROR", 500)

