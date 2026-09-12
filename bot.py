import os 
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Referal düşündirişleri ýazjak toparyňyzyň ssylkasy
TUTORIAL_GROUP_LINK = "https://t.me/referal_bolmak"

# Administratoryň Telegram ID-si (Öz Telegram ID-ňizi şu ýere ýazyň)
ADMIN_ID = 6970856886  # <--- Öz Telegram ID-ňizi ýazmagy unutmaň!

# Premium gruppanyň gizlin ssylkasy
PREMIUM_GROUP_LINK = "https://t.me/+SizinGizlinSsylkanyz"

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
        await query.edit_message_text(
            text="🚀 FX_Nexor Bot-a hoş geldiňiz!\n\n"
                 "💎 Forex & XAUUSD  Signals and News\n"
                 "📈 Professional Market Analysis\n"
                 "🔔 Real-Time Trading Signals\n\n"
                 "Aşakdaky menýudan saýla:",
            reply_markup=reply_markup
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
        text = (
            "💎 **Eger siz premium agza bolanyňyzda:**\n\n"
            "• Signallar - günde 5 den 10 na çenli signal alarsyňyz.\n\n"
            "• Bazara we kriptowalýuta täsir edip biljek habarlar ýetiriler.\n\n"
            "• Risk menejment hasaplanar.\n\n"
            "• Wideojaňda real time söwda ederis.\n\n"
            "• Her hepdäniň soňunda netije ýagny gazanalynan we ýitirlen pipsler hasaplanar.\n\n"
            "Özüñize amatly bolan usuly saýlaň:"
        )
        premium_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤝 Meniň referalym bol", callback_data="ref_method")],
            [InlineKeyboardButton("💳 Satyn al", callback_data="buy_method")],
            [InlineKeyboardButton("🔙 Yza", callback_data="back_to_start")]
        ])
        await query.edit_message_text(text=text, reply_markup=premium_keyboard, parse_mode="Markdown")
        return
    elif query.data == "ref_method":
        text = (
            "🤝 **Referal arkaly Premium almak:**\n\n"
            "1. Aşakdaky düwme arkaly görkezme toparyna girip hasap açyň.\n"
            "2. Depozit goýanyňyzdan soň, **Broker ID nomeriňizi** ýa-da hasabdaky **poçtaňyzy** şu çata hat arkaly iberiň."
        )
        ref_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤔 Nädip referalyň bolmaly!?", url=TUTORIAL_GROUP_LINK)],
            [InlineKeyboardButton("📥 Broker ID iber", callback_data="send_id_prompt")],
            [InlineKeyboardButton("🔙 Yza", callback_data="premium")]
        ])
        await query.edit_message_text(text=text, reply_markup=ref_keyboard, parse_mode="Markdown")
        return
    elif query.data == "send_id_prompt":
        context.user_data["waiting_for_broker_id"] = True
        text = "Ýaxşy! Indi brokerde açan **ID nomeriňizi** ýa-da **hasaba bagly poçtaňyzy** şu çata hat arkaly ýazyp iberiň:"
        await query.edit_message_text(text, reply_markup=back_keyboard)
        return
    elif query.data == "buy_method":
        text = "💳 **Satyn almak:**\n\nBu bölüm ýakynda işläp başlar."
        await query.edit_message_text(text, reply_markup=back_keyboard, parse_mode="Markdown")
        return
    
    # Admin tassyklama ýa-da rad etme düwmeleri
    elif query.data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Bu düwmäni diňe admin basyp biler!", show_alert=True)
            return
        
        target_user_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🎉 Gutlaýarys! Siziň broker ID maglumatyňyz tassyksyny tapdy. Premium toparyň ssylkasy:\n\n{PREMIUM_GROUP_LINK}"
            )
            await query.edit_message_text(text=f"✅ Ulanyjy (ID: `{target_user_id}`) tassyksyny aldy we ssylka iberildi.", parse_mode="Markdown")
        except Exception:
            await query.edit_message_text(text="⚠️ Ulanyja habar ýetirip bolmady (boti bloklan bolmagy mümkin).")
        return

    elif query.data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Bu düwmäni diňe admin basyp biler!", show_alert=True)
            return
        
        target_user_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ Bagyşlaň, siz iberen maglumatyňyz (broker ID ýa-da depozit şerti) tassyklanmadi. Ýalňyşlyk bar bolsa gaýtadan barlaň."
            )
            await query.edit_message_text(text=f"❌ Ulanyjy (ID: `{target_user_id}`) üçin sorag rad edildi.")
        except Exception:
            await query.edit_message_text(text="⚠️ Ulanyja habar ýetirip bolmady.")
        return

    else:
        text = "❓ Näbelli bölüm."
        await query.edit_message_text(text, reply_markup=back_keyboard)

# Ulanyjynyň ýazan broker ID / Poçta maglumatyny kabul edip admina ugratmak
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Ýok"
    text = update.message.text

    if context.user_data.get("waiting_for_broker_id"):
        context.user_data["waiting_for_broker_id"] = False
        
        admin_text = (
            f"🔔 **Täze Premium Broker Barlag Soragy!**\n\n"
            f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
            f"📋 Broker ID / Poçta: `{text}`"
        )
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tassykla we Ssylka Iber", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Rad Et", callback_data=f"reject_{user_id}")
            ]
        ])
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
            await update.message.reply_text("✅ Maglumatyňyz admina iberildi! Barlanylandan soň premium gruppanyň ssylkasy size iberiler.")
        except Exception:
            await update.message.reply_text("⚠️ Ýalňyşlyk ýüze çykdy, admin ID-niň dogrulygyny barlaň.")

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN tapylmady!")

    Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Meta5Signals Bot started with auto-verification workflow!")
    application.run_polling()

if __name__ == "__main__":
    main()
