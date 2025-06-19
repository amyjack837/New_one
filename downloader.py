import os
import uuid
import aiohttp
from yt_dlp import YoutubeDL

async def download_video(url):
    temp_id = uuid.uuid4().hex
    output_path = f"/tmp/{temp_id}.%(ext)s"
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, None
    except Exception as e:
        print(f"[yt_dlp failed] {e}")

    apis = [
        f"https://saveig.app/api/ajaxSearch?url={url}",
        f"https://api.sssgram.com/api/download?url={url}"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        for api in apis:
            try:
                async with session.get(api, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        link = data.get("url") or data.get("video") or data.get("link")
                        if link:
                            return None, link
            except Exception as e:
                print(f"[API fallback error] {e}")
    return None, None
