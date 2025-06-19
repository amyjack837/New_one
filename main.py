import os
import re
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
import instaloader
from keep_alive import keep_alive

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "7553973906:AAGJiUGopXm7wqg6boU0Sv-fTbO1OzutyiA")

app = Client("bot", bot_token=BOT_TOKEN)

URL_REGEX = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s)\]\}>]*'

YDL_OPTS = {
    'outtmpl': 'downloads/%(title).100s.%(ext)s',
    'format': 'bestvideo+bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'merge_output_format': 'mp4',
    'nocheckcertificate': True,
    'retries': 3
}

os.makedirs("downloads", exist_ok=True)

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text("👋 Send any YouTube or Instagram link to download.")

@app.on_message(filters.text & filters.private)
async def download(_, message: Message):
    urls = re.findall(URL_REGEX, message.text)
    if not urls:
        await message.reply_text("❌ No valid link found.")
        return

    for url in urls:
        try:
            await message.reply_text(f"📥 Downloading: {url}")
            file_path = await download_media(url)
            await message.reply_video(file_path) if file_path.endswith(".mp4") else await message.reply_document(file_path)
            os.remove(file_path)
        except Exception as e:
            logging.warning(f"yt_dlp failed: {e}")
            await message.reply_text("⚠️ Trying fallback method...")
            try:
                file_path = await download_instagram(url)
                await message.reply_document(file_path)
                os.remove(file_path)
            except Exception as ex:
                logging.error(f"Fallback failed: {ex}")
                await message.reply_text("❌ Failed to download media.")

async def download_media(url):
    loop = asyncio.get_event_loop()
    with YoutubeDL(YDL_OPTS) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        return ydl.prepare_filename(info)

async def download_instagram(url):
    L = instaloader.Instaloader(dirname_pattern="downloads", save_metadata=False)
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target=shortcode)
    for file in os.listdir(shortcode):
        return os.path.join(shortcode, file)

if __name__ == "__main__":
    keep_alive()
    app.run()
