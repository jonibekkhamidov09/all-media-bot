import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋\n"
        "Menga video havolasini yuboring.\n"
        "Men uni yuklab berishga harakat qilaman."
    )
async def download_media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    url = update.message.text.strip()
    if not url.startswith(("https://", "http://")):
        await update.message.reply_text(
            "Iltimos, to'g'ri video havolasini yuboring."
        )
        return
    msg = await update.message.reply_text("⏳ Yuklanmoqda...")
    try:
        options = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "noplaylist": True,
            "max_filesize": 49_000_000,
        }
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
        if not os.path.isfile(filepath):
            await msg.edit_text("Fayl topilmadi.")
            return
        with open(filepath, "rb") as video:
            await update.message.reply_video(video=video)
        os.remove(filepath)
        await msg.delete()
    except Exception:
        logging.exception("Media yuklashda xato")
        await msg.edit_text(
            "❌ Yuklab bo'lmadi. Boshqa havolani sinab ko'ring."
        )
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN sozlanmagan!")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download_media)
    )
    app.run_polling()
if __name__ == "__main__":
    main()