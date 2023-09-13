from tempfile import NamedTemporaryFile
from os import environ, path
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    Application,
    filters,
)

from pypdf import PdfReader, PdfWriter, PasswordType
import epson_connect as ec

KEY_FILE = "./keys.txt"

TELEGRAM_ALLOWED_CHAT_IDS = [
    int(chat_id.strip()) for chat_id in environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",") if chat_id.strip()
]

epson_client = ec.Client(
    printer_email=environ.get("EPSON_CONNECT_API_PRINTER_EMAIL"),
    client_id=environ.get("EPSON_CONNECT_API_CLIENT_ID"),
    client_secret=environ.get("EPSON_CONNECT_API_CLIENT_SECRET"),
)


async def incoming_pdf_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (chat_id := update.message.chat_id) not in TELEGRAM_ALLOWED_CHAT_IDS:
        logging.warning(f"Chat {str(chat_id)} not allowed")
        await update.message.reply_text(f"🚫 Questo bot non è abilitato per questa chat.\nChat ID: {str(chat_id)}")
        return
    keys_to_try = []
    if path.isfile(KEY_FILE):
        with open(KEY_FILE, "r") as keys_file:
            keys_to_try.extend(keys_file.readlines())
    if update.message.caption:
        keys_to_try.insert(0, update.message.caption)

    with NamedTemporaryFile(suffix=".pdf") as temp_file:
        logging.info("Downloading PDF...")
        await update.message.reply_text("📃 Elaboro il tuo PDF...")
        telegram_file = await update.message.document.get_file()
        await telegram_file.download_to_drive(temp_file.name)
        logging.info("PDF downloaded")

        pdf_reader = PdfReader(temp_file)

        if pdf_reader.is_encrypted:
            logging.info("PDF is encrypted, trying to decrypt...")
            for key in keys_to_try:
                if pdf_reader.decrypt(key) is not PasswordType.NOT_DECRYPTED:
                    logging.info(f"PDF decrypted with key {key}")
                    await update.message.reply_text("🎉 PDF decifrato con successo!")
                    break
            else:
                logging.warning("No key worked")
                await update.message.reply_text(
                    "🔐 Nessuna chiave fornita ha funzionato. Scrivi la chiave del PDF nella didascalia del messaggio."
                )
                return

        pdf_writer = PdfWriter()
        pdf_writer.clone_document_from_reader(pdf_reader)

        pdf_writer.write(temp_file.name)
        job_id = epson_client.printer.print(temp_file.name)
        await update.message.reply_text(f"🖨️ Il PDF è ora in stampa! (ID del job: {job_id})")


app: Application = ApplicationBuilder().token(environ.get("TELEGRAM_BOT_TOKEN")).build()

app.add_handler(MessageHandler(filters=filters.Document.PDF, callback=incoming_pdf_handler))

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING)

app.run_polling()
