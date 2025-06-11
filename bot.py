import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from yt_dlp import YoutubeDL

TELEGRAM_FILE_LIMIT = 50 * 1024 * 1024  # 50MB

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /convert <YouTube URL>")
        return

    url = context.args[0]
    await update.message.reply_text("Downloading and converting...")

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "320",
            }],
            "noplaylist": True,
        }

        status_msg = await update.message.reply_text("📩 Starting download...")

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict).replace(".webm", ".m4a").replace(".m4a.m4a", ".m4a")

        await status_msg.edit_text("🎵 Converting...")

        # After conversion
        file_size = os.path.getsize(filename)
        if file_size > TELEGRAM_FILE_LIMIT:
            await status_msg.edit_text("❌ File too large to send (limit: 50MB).")
            os.remove(filename)
            return

        await status_msg.edit_text("📤 Uploading...")
        await update.message.reply_audio(audio=open(filename, "rb"))

        os.remove(filename)
        await status_msg.edit_text("✅ Job Done!")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"Error: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("convert", convert))
    print("Bot is running...")
    app.run_polling()