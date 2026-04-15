from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes 
from dotenv import load_dotenv
import os, anthropic, base64
load_dotenv()
telegram_api = os.getenv("TELEGRAM")
claude_api = os.getenv("CLAUDE")
client = anthropic.Anthropic(api_key=claude_api)

async def pdf_erhalten(update, context): 
    datei = await update.message.document.get_file()
    await datei.download_to_drive("datei.pdf")
    x = open ("datei.pdf","rb").read()
    pdf_data = base64.b64encode(x).decode("utf-8")
    antwort = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": "Fasse mir diese Datei zusammen und gebe mir (falls nötig) passende Beispele wenn noch keine vorhanden sind in der Folie. Danach schreibst du mir Karteikarten zu dem entsprechenden Thema mit Fragen, Erklärungen und Lösungen. Immer alles auf Deutsch. " #ist nur vorrübergehend
                    }
                ]
            }
        ]
    )
    text = antwort.content[0].text
    for i in range(0, len(text), 4096):
        await update.message.reply_text(text[i:i+4096])

start = Application.builder().token(telegram_api).build()
start.add_handler(MessageHandler(filters.Document.PDF, pdf_erhalten))
start.run_polling()
