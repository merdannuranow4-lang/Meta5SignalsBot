import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Referal düşündirişleri ýazjak toparyňyzyň ssylkasy
TUTORIAL_GROUP_LINK = "https://t.me/referal_bolmak"

# Administratoryň Telegram ID-si
ADMIN_ID = 6970856886

# Premium gruppanyň gizlin ssylkasy
PREMIUM_GROUP_LINK = "https://t.me/+ydp8yB7HNgNkNzJi"
PREMIUM_GROUP_CHAT_ID = os.getenv("-1004401546667")

app = Flask(__name__)

@app.route("/")
def home():
    return "Meta5Signals Bot is running! 🚀"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- BAZA BILEN IŞLEMEK (SQLite) ---
def init_db():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subs (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            plan_name TEXT,
            expire_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_subscription(user_id, username, days):
    # Eger days 0 ýa-da oňa meňzeş bolsa (m/s referal üçin wagt çäklendirmesi ýok bolsa), uzak wagt ýa-da null saklap bolar
    if days > 0:
        expire_date = datetime.now() + timedelta(days=days)
        expire_str = expire_date.strftime("%Y-%m-%d %H:%M:%S")
        plan_text = f"{days} gün"
    else:
        # Referal üçin wagt çäklendirmesi yok ýa-da uzak möhlet (mysal üçin 3650 gün - 10 ýyl)
        expire_date = datetime.now() + timedelta(days=3650)
        expire_str = expire_date.strftime("%Y-%m-%d %H:%M:%S")
        plan_text = "Referal (Wagtsyz)"

    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO subs (user_id, username, plan_name, expire_date)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, plan_text, expire_str))
    conn.commit()
    conn.close()

def get_expired_users():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT user_id FROM subs WHERE expire_date <= ? AND plan_name != 'Referal (Wagtsyz)'", (now_str,))
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def remove_expired_user_from_db(user_id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subs WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# ----------------------------------

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
        "💎 Forex & XAUUSD Signals and News\n"
        "📈 Professional Market Analysis\n"
        "🔔 Real-Time Trading Signals\n\n"
        "Aşakdaky menýudan saýla:",
        reply_markup=reply_markup
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Yza", callback_data="back_to_start")]
    ])

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
                 "💎 Forex & XAUUSD Signals and News\n"
                 "📈 Professional Market Analysis\n"
                 "🔔 Real-Time Trading Signals\n\n"
                 "Aşakdaky menýudan saýla:",
            reply_markup=reply_markup
        )
        return

    if query.data == "results":
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
        context.user_data["waiting_for_type"] = "broker_id"
        text = "Ýaxşy! Indi brokerde açan **ID nomeriňizi** ýa-da **hasaba bagly poçtaňyzy** şu çata hat arkaly ýazyp iberiň:"
        await query.edit_message_text(text, reply_markup=back_keyboard)
        return

    elif query.data == "buy_method":
        text = "💳 **Satyn almak üçin möhleti saýlaň:**"
        buy_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Aýlyk", callback_data="plan_30")],
            [InlineKeyboardButton("3 Aýlyk", callback_data="plan_90")],
            [InlineKeyboardButton("6 Aýlyk", callback_data="plan_180")],
            [InlineKeyboardButton("1 Ýyllyk", callback_data="plan_365")],
            [InlineKeyboardButton("🔙 Yza", callback_data="premium")]
        ])
        await query.edit_message_text(text=text, reply_markup=buy_keyboard, parse_mode="Markdown")
        return

    elif query.data.startswith("plan_"):
        days = query.data.split("_")[1]
        
        prices = {"30": "40", "90": "100", "180": "180", "365": "300"}
        price = prices.get(days, "40")
        month_label = {"30": "bir aýlyk", "90": "üç aýlyk", "180": "alty aýlyk", "365": "bir ýyllyk"}.get(days, "bir aýlyk")

        context.user_data["waiting_for_type"] = f"payment_{days}"

        text = (
            f"Siz {month_label} premium satyn alýarsyňyz!\n\n"
            f"Bahasy: 💲{price}\n"
            f"Töleg salgysy: 📌 USDT-TRC20\n"
            f"Töleg kody: 🔑 `TXx9GWMG3JZ7NqEz76f7cXSbr4TFFjbNZx`\n\n"
            "Tölegi doly tamamlanyňyzdan soň töleg edenligiňiz barada skrinşody hem-de UID kodyňyzy şu çata ýazyň."
        )
        plan_back = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Yza", callback_data="buy_method")]])
        await query.edit_message_text(text=text, reply_markup=plan_back, parse_mode="Markdown")
        return

    # Admin Tassyklama / Ret etme bölümleri
    elif query.data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Bu düwmäni diňe admin basyp biler!", show_alert=True)
            return
        
        parts = query.data.split("_")
        target_user_id = int(parts[1])
        
        # Eger referal bolsa (days ýok ýa-da 0 berlen bolsa)
        if len(parts) > 2 and parts[2] != "ref":
            days = int(parts[2])
            add_subscription(target_user_id, "Unknown", days)
            success_msg = f"✅ Ulanyjy (ID: `{target_user_id}`) tassyksyny aldy we {days} günlük premium berildi."
        else:
            # Referal üçin wagt çäklendirmesi ýok (wagtsyz)
            add_subscription(target_user_id, "Unknown", 0)
            success_msg = f"✅ Referal ulanyjy (ID: `{target_user_id}`) tassyksyny aldy (Wagtsyz)."

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🎉 Gutlaýarys! Siziň maglumatyňyz tassyksyny tapdy. Premium toparyň ssylkasy:\n\n{PREMIUM_GROUP_LINK}"
            )
            await query.edit_message_text(text=success_msg, parse_mode="Markdown")
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
                text="❌ Bagyşlaň, siz iberen maglumat ýa-da skrinşod tassyklanmadi. Ýalňyşlyk bar bolsa gaýtadan barlaň."
            )
            await query.edit_message_text(text=f"❌ Ulanyjy (ID: `{target_user_id}`) üçin sorag rad edildi.")
        except Exception:
            await query.edit_message_text(text="⚠️ Ulanyja habar ýetirip bolmady.")
        return

# Ulanyjynyň iberen broker ID-si ýa-da Töleg skrinşodyny / habaryny kabul etmek
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Ýok"
    waiting_type = context.user_data.get("waiting_for_type")

    if not waiting_type:
        return

    if waiting_type == "broker_id":
        context.user_data["waiting_for_type"] = None
        text = update.message.text or "Surat ýa-da maglumat"
        
        admin_text = (
            f"🔔 **Täze Referal Broker Barlag Soragy!**\n\n"
            f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
            f"📋 Broker ID / Poçta: `{text}`"
        )
        # REFRAL ÜÇIN "30 gün" AÝRYLDY, DINE TASSYKLA WE RAD ET DÜWMELERI GOÝULDY
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tassykla", callback_data=f"approve_{user_id}_ref"),
                InlineKeyboardButton("❌ Rad Et", callback_data=f"reject_{user_id}")
            ]
        ])
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
            await update.message.reply_text("✅ Maglumatyňyz admina iberildi! Barlanylandan soň premium gruppanyň ssylkasy size iberiler.")
        except Exception:
            await update.message.reply_text("⚠️ Ýalňyşlyk ýüze çykdy, admin ID-niň dogrulygyny barlaň.")

    elif waiting_type.startswith("payment_"):
        days = waiting_type.split("_")[1]
        context.user_data["waiting_for_type"] = None
        
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tassykla we Ssylka Iber", callback_data=f"approve_{user_id}_{days}"),
                InlineKeyboardButton("❌ Rad Et", callback_data=f"reject_{user_id}")
            ]
        ])

        try:
            if update.message.photo:
                photo_file_id = update.message.photo[-1].file_id
                caption = (
                    f"💳 **Täze Töleg Skrinşody!** ({days} günlük paket)\n\n"
                    f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
                    f"💬 Goşmaça: {update.message.caption or 'Ýok'}"
                )
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=caption, reply_markup=admin_keyboard, parse_mode="Markdown")
            else:
                text_content = update.message.text or "Maglumat ýok"
                admin_text = (
                    f"💳 **Täze Töleg Maglumaty!** ({days} günlük paket)\n\n"
                    f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
                    f"📋 UID / Maglumat: `{text_content}`"
                )
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")

            await update.message.reply_text("✅ Skrinşodyňyz we maglumatyňyz admina iberildi! Tassyklanandan soň size habar berler.")
        except Exception as e:
            await update.message.reply_text("⚠️ Maglumaty admina ugratmakda ýalňyşlyk ýüze çykdy.")

async def check_subscriptions_loop(application):
    while True:
        await asyncio.sleep(3600)
        expired_users = get_expired_users()
        for user_id in expired_users:
            if PREMIUM_GROUP_CHAT_ID:
                try:
                    await application.bot.ban_chat_member(chat_id=PREMIUM_GROUP_CHAT_ID, user_id=user_id)
                    await application.bot.unban_chat_member(chat_id=PREMIUM_GROUP_CHAT_ID, user_id=user_id)
                except Exception:
                    pass
            
            try:
                await application.bot.send_message(
                    chat_id=user_id,
                    text="⚠️ Siziň premium agzalyk möhletiniz gutardy! Täzeden agza bolmak üçin /start düwmesine basyň."
                )
            except Exception:
                pass
            
            remove_expired_user_from_db(user_id)

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN tapylmady!")

    init_db()
    Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    async def post_init(app_instance):
        asyncio.create_task(check_subscriptions_loop(app_instance))

    application.post_init = post_init

    print("Meta5Signals Bot started successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()
