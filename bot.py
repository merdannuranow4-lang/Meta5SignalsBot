import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Meta5Signals Premium Bot is running! 🚀"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📊 Signallar", url="https://t.me/meta5signals_XAUUSD "),
            InlineKeyboardButton("🥇 XAUUSD", callback_data="gold")
        ],
        [
            InlineKeyboardButton("📈 Analiz", callback_data="analysis"),
            InlineKeyboardButton("🏆 Netijeler", callback_data="results")
        ],
        [
            InlineKeyboardButton("💎 Premium Agzalyk", callback_data="premium")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 Meta5Signals Premium Bot-a hoş geldiňiz!\n\n"
        "💎 Forex & XAUUSD Premium Signals\n"
        "📈 Professional Market Analysis\n"
        "🔔 Real-Time Trading Signals\n\n"
        "Aşakdaky menýudan saýla:",
        reply_markup=reply_markup
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signals":
        text = "📊 Premium Signallar\n\nHäzirlikçe täze signal ýok."
    elif query.data == "gold":
        text = "🥇 XAUUSD\n\nAltyn boýunça signallar şu ýerde görkeziler."
    elif query.data == "analysis":
        text = "📈 Bazar Analizi\n\nProfessional analizler şu ýerde bolar."
    elif query.data == "results":
        text = "🏆 Signal Netijeleri\n\nNetijeler şu ýerde görkeziler."
    elif query.data == "premium":
        text = "💎 Premium Agzalyk\n\nPremium hyzmat ýakynda elýeterli bolar."
    else:
        text = "❓ Näbelli bölüm."

    await query.edit_message_text(text)

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN tapylmady!")

    Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))

    print("Meta5Signals Bot started!")
    application.run_polling()

if __name__ == "__main__":
    main()
