import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.filters import CommandStart
from aiogram import F
from downloader import download_video
from utils import extract_links

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Secure way to load your bot token

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.reply("📥 Send me any Instagram or YouTube link!")

@dp.message(F.text)
async def handle_links(message: types.Message):
    links = extract_links(message.text)
    if not links:
        return await message.reply("❌ No valid link found.")

    for url in links:
        await message.reply(f"⏳ Downloading from: {url}")
        filepath, fallback_link = await download_video(url)
        if filepath:
            try:
                await message.reply_document(FSInputFile(filepath))
            except Exception as e:
                await message.reply(f"⚠️ Couldn't send file. Error: {e}")
            finally:
                os.remove(filepath)
        elif fallback_link:
            await message.reply(f"✅ [Click to Download]({fallback_link})", parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply("❌ Failed to download.")

if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
