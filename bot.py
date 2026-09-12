import os 
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Meta5Signals Bot is running! 🚀"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📊 Signals", url="https://t.me/meta5signals_XAUUSD"),
            InlineKeyboardButton("🗞️ News", url="https://t.me/GoldFnews")
        ],
        [
            InlineKeyboardButton("👥 Chat group", url="https://t.me/meta5signal_chat"),
            InlineKeyboardButton("🌐 Website", callback_data="results")
        ],
        [
            InlineKeyboardButton("💎 Premium Agzalyk", callback_data="premium")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 FX_Nexor Bot-a hoş geldiňiz!\n\n"
        "💎 Forex & XAUUSD  Signals and News\n"
        "📈 Professional Market Analysis\n"
        "🔔 Real-Time Trading Signals\n\n"
        "Aşakdaky menýudan saýla:",
        reply_markup=reply_markup
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_start":
        await query.edit_message_text(
            text=START_TEXT,
            reply_markup=get_start_keyboard()
        )
        return
    
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Yza", callback_data="back_to_start")]
    ])
    
    if query.data == "signals":
        text = "📊 Premium Signallar\n\nHäzirlikçe täze signal ýok."
        await query.edit_message_text(text, reply_markup=back_keyboard)
    elif query.data == "gold":
        text = "🥇 XAUUSD\n\nAltyn boýunça signallar şu ýerde görkeziler."
        await query.edit_message_text(text, reply_markup=back_keyboard)
    elif query.data == "analysis":
        text = "📈 Bazar Analizi\n\nProfessional analizler şu ýerde bolar."
        await query.edit_message_text(text, reply_markup=back_keyboard)
    elif query.data == "results":
        text = "🌐 Website\n\nHäzirlikçe el ýeterli däl."
        await query.edit_message_text(text, reply_markup=back_keyboard)
    elif query.data == "premium":
        text = "💎 **Premium Agzalyk Bölümi**\n\nÖzüñize amatly bolan usuly saýlaň:"
        premium_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤝 Meniň referalym bol", callback_data="ref_method")],
            [InlineKeyboardButton("💳 Satyn al", callback_data="buy_method")],
            [InlineKeyboardButton("🔙 Yza", callback_data="back_to_start")]
        ])
        await query.edit_message_text(text=text, reply_markup=premium_keyboard, parse_mode="Markdown")
        return
    elif query.data == "ref_method":
        text = "🤝 **Referal arkaly Premium almak:**\n\n1. Brokerde hasap açyň.\n2. Depozit goýuň."
        await query.edit_message_text(text, reply_markup=back_keyboard, parse_mode="Markdown")
        return
    elif query.data == "buy_method":
        text = "💳 **Satyn almak:**\n\nBu bölüm ýakynda işläp başlar."
        await query.edit_message_text(text, reply_markup=back_keyboard, parse_mode="Markdown")
        return
    else:
        text = "❓ Näbelli bölüm."
        await query.edit_message_text(text, reply_markup=back_keyboard)

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
