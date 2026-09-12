import os 
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Referal düşündirişleri ýazjak toparyňyzyň ssylkasy
TUTORIAL_GROUP_LINK = "https://t.me/referal_bolmak"

# Administratoryň Telegram ID-si (Öz Telegram ID-ňizi şu ýere ýazyň)
ADMIN_ID = 6970856886  # <--- Öz Telegram ID-ňizi ýazmagy unutmaň!

# Premium gruppanyň ID-si (Bot şol grupda admin bolmaly we çakylyk döretmäge hukugy bolmaly)
PREMIUM_GROUP_ID = -1004401546667  # <--- Öz Premium gruppanyňyzyň ID-sini ýazyň

# Kripto gapjyk adresiniz (Hemişelik üýtgemeýän adresiňiz)
USDT_WALLET_ADDRESS = "TFK7Z1FtBiBu2AnLQhzRtdZR43TsffWtCz"

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
        context.user_data["action_type"] = "broker_id"
        text = "Ýaxşy! Indi brokerde açan **ID nomeriňizi** ýa-da **hasaba bagly poçtaňyzy** şu çata hat arkaly ýazyp iberiň:"
        await query.edit_message_text(text, reply_markup=back_keyboard)
        return
    elif query.data == "buy_method":
        text = "💳 **Tarif saýlaň:**\n\nÖzüňize laýyk gelýän premium möhletini saýlap, töleg ediň:"
        buy_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Aýlyk", callback_data="plan_30")],
            [InlineKeyboardButton("3 Aýlyk", callback_data="plan_90")],
            [InlineKeyboardButton("6 Aýlyk", callback_data="plan_180")],
            [InlineKeyboardButton("1 Ýyllyk", callback_data="plan_365")],
            [InlineKeyboardButton("🔙 Yza", callback_data="premium")]
        ])
        await query.edit_message_text(text=text, reply_markup=buy_keyboard, parse_mode="Markdown")
        return
    
    # Tarif saýlanylanda
    elif query.data.startswith("plan_"):
        days = int(query.data.split("_")[1])
        context.user_data["action_type"] = "buy_txid"
        context.user_data["subscription_days"] = days
        
        plan_name = {30: "1 Aýlyk", 90: "3 Aýlyk", 180: "6 Aýlyk", 365: "1 Ýyllyk"}.get(days, f"{days} Günlük")
        
        text = (
            f"💳 **Siz saýladyňyz:** {plan_name}\n\n"
            f"Töleg etmek üçin aşakdaky USDT (TRC20) adresimize iberiň:\n"
            f"`{USDT_WALLET_ADDRESS}`\n\n"
            f"Töleg edip bolanyňyzdan soň, tranzaksiýa belgisini (**TxID**) ýa-da töleg skrinşodyny şu çata iberiň:"
        )
        await query.edit_message_text(text=text, reply_markup=back_keyboard, parse_mode="Markdown")
        return

    # Admin tassyklama (approve_)
    elif query.data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Bu düwmäni diňe admin basyp biler!", show_alert=True)
            return
        
        parts = query.data.split("_")
        target_user_id = int(parts[1])
        
        try:
            if len(parts) > 2:
                # Kripto satyn alyş (möhletli çakylyk ssylkasy)
                days = int(parts[2])
                expire_time = datetime.now() + timedelta(days=days)
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=PREMIUM_GROUP_ID,
                    expire_date=expire_time,
                    member_limit=1
                )
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎉 Gutlaýarys! Tölegiňiz tassyksyny tapdy ({days} günlük). Premium toparyň wagtlaýyn ssylkasy:\n\n{invite_link.invite_link}"
                )
            else:
                # Referal arkaly gelenler (adaty çakylyk ssylkasy)
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=PREMIUM_GROUP_ID,
                    member_limit=1
                )
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎉 Gutlaýarys! Siziň broker ID maglumatyňyz tassyksyny tapdy. Premium toparyň ssylkasy:\n\n{invite_link.invite_link}"
                )
                
            await query.edit_message_text(text=f"✅ Ulanyjy (ID: `{target_user_id}`) tassyksyny aldy we ssylka iberildi.", parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ Ýalňyşlyk ýüze çykdy: {e}")
        return

    # Admin rad etme (reject_)
    elif query.data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Bu düwmäni diňe admin basyp biler!", show_alert=True)
            return
        
        target_user_id = int(parts[1]) if 'parts' in locals() else int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ Bagyşlaň, iberen maglumatyňyz / tölegiňiz tassyklanmadi. Ýalňyşlyk bar bolsa gaýtadan barlaň."
            )
            await query.edit_message_text(text=f"❌ Ulanyjy (ID: `{target_user_id}`) üçin sorag rad edildi.")
        except Exception:
            await query.edit_message_text(text="⚠️ Ulanyja habar ýetirip bolmady.")
        return

    else:
        text = "❓ Näbelli bölüm."
        await query.edit_message_text(text, reply_markup=back_keyboard)

# Ulanyjynyň iberen tekst ýa-da surat (skrinşod) maglumatyny kabul edip admina ugratmak
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Ýok"
    action_type = context.user_data.get("action_type")

    if not action_type:
        return  # Eger ulanyjy hiç hilli barlag garaşylýan ýerde däl bolsa, jogap bermeli däl

    # Tekst ýa-da surat (photo) barlygyny barlamak
    text_content = update.message.text
    photo_file_id = None
    
    if update.message.photo:
        # Surat iberilen bolsa, iň uly rewolýusion file_id-sini alýarys
        photo_file_id = update.message.photo[-1].file_id
        text_content = update.message.caption or "Skrinşod iberildi (tekst ýok)"

    if action_type == "broker_id":
        context.user_data["action_type"] = None
        
        admin_text = (
            f"🔔 **Täze Premium Broker Barlag Soragy!**\n\n"
            f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
            f"📋 Broker ID / Poçta: `{text_content}`"
        )
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tassykla we Ssylka Iber", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Rad Et", callback_data=f"reject_{user_id}")
            ]
        ])
        
        try:
            if photo_file_id:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
            
            await update.message.reply_text("✅ Maglumatyňyz admina iberildi! Barlanylandan soň premium gruppanyň ssylkasy size iberiler.")
        except Exception:
            await update.message.reply_text("⚠️ Ýalňyşlyk ýüze çykdy, admin ID-niň dogrulygyny barlaň.")

    elif action_type == "buy_txid":
        days = context.user_data.get("subscription_days", 30)
        context.user_data["action_type"] = None
        context.user_data["subscription_days"] = None
        
        plan_name = {30: "1 Aýlyk", 90: "3 Aýlyk", 180: "6 Aýlyk", 365: "1 Ýyllyk"}.get(days, f"{days} Günlük")

        admin_text = (
            f"💳 **Täze Krypto Töleg Barlag Soragy!**\n\n"
            f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
            f"📦 Saýlanan Tarif: {plan_name}\n"
            f"🧾 Töleg maglumaty / TxID: `{text_content}`"
        )
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tassykla we Ssylka Iber", callback_data=f"approve_{user_id}_{days}"),
                InlineKeyboardButton("❌ Rad Et", callback_data=f"reject_{user_id}")
            ]
        ])
        
        try:
            if photo_file_id:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
            
            await update.message.reply_text("✅ Töleg maglumatyňyz admina iberildi! Barlanylandan soň wagtlaýyn premium ssylkasy size iberiler.")
        except Exception:
            await update.message.reply_text("⚠️ Ýalňyşlyk ýüze çykdy, admin ID-niň dogrulygyny barlaň.")

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN tapylmady!")

    Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    # Indi hem tekst hem-de skrinşod (surat) habarlaryny birbada kabul eder ýaly filters üýtgedildi
    application.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_message))

    print("Meta5Signals Bot started successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()

