import os
import re
# pyrefly: ignore [missing-import]
import httpx
# pyrefly: ignore [missing-import]
from telegram import Update
# pyrefly: ignore [missing-import]
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Environment configuration:

BOT_TOKEN = os.getenv("BOT_TOKEN")
INGEST_DIR = os.getenv("INGEST_DIR")
CWA_URL = os.getenv("CWA_URL")

DOWLOAD_DIR = "/tmp/ingest_bot_downloads"
if not os.path.exists(DOWLOAD_DIR):
    os.makedirs(DOWLOAD_DIR)


# Basic functions:

async def is_epub(file_path: str) -> bool:
    if file_path.lower().endswith('.epub'):
        return True
    return False

async def size_ok(file_size: int) -> bool:
    # CWA has a 20MB limit for ingested files.
    if file_size > 20 * 1024 * 1024:
        return False
    return True

async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not await is_epub(doc.file_name):
        await update.message.reply_text("Please send an EPUB file.")
        return
    
    if not await size_ok(doc.file_size):
        await update.message.reply_text("File size exceeds the 20MB limit.")
        return

    doc_name = re.sub(r'[ /\\,:*?"<>|&$]', "", doc.file_name)

    # Download the file to a temporary location to prevent issues with CWA ingest process.
    tmp_doc = await doc.get_file()
    FILE_TEMP_DIR = f"{DOWLOAD_DIR}/{doc_name}"
    await tmp_doc.download_to_drive(FILE_TEMP_DIR)

    # Move the file to the ingest directory.
    FILE_CWA_DIR = f"{INGEST_DIR}/{doc_name}"
    os.system(f"mv {FILE_TEMP_DIR} {FILE_CWA_DIR}")
    await update.message.reply_text(f"File '{doc_name}' moved to ingest directory. It should be processed by CWA soon.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not CWA_URL:
        await update.message.reply_text("⚠️ CWA_URL is not configured.")
        return
    
    try:
        await update.message.reply_text(f"Checking connectivity to CWA at {CWA_URL}...")
        response = httpx.get(CWA_URL, timeout=10)
        if response.status_code < 400:
            await update.message.reply_text(" CWA is reachable.")
        else:
            await update.message.reply_text(f" CWA responded with status code {response.status_code}.")
    except httpx.RequestError as e:
        await update.message.reply_text(f"❌ CWA is not reachable: {e}")

# Handler setup:

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the CWA Ingest Bot! Please send me an EPUB file (20MB max) to ingest it into CWA.")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ping(update, context)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start - Start the bot\n/ping - Check CWA connectivity\n/help - Show this help message\n\nJust send an EPUB file to ingest it into your CWA library.")

# Main function:
def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable is not set.")
        return
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
