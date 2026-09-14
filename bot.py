import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

TUTORIAL_GROUP_LINK = "https://t.me/referal_bolmak"

ADMIN_ID = 6970856886

PREMIUM_GROUP_LINK = "https://t.me/+ydp8yB7HNgNkNzJi"
PREMIUM_GROUP_CHAT_ID = -1004401546667

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
    if days > 0:
        expire_date = datetime.now() + timedelta(days=days)
        expire_str = expire_date.strftime("%Y-%m-%d %H:%M:%S")
        plan_text = f"{days} gün"
    else:
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

    cursor.execute(
        "SELECT user_id FROM subs WHERE expire_date <= ? AND plan_name != 'Referal (Wagtsyz)'",
        (now_str,)
    )

    users = [row[0] for row in cursor.fetchall()]
    conn.close()

    return users


def remove_expired_user_from_db(user_id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM subs WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


# ----------------------------------
# ULANYJYNYŇ PROFILI
# ----------------------------------

def get_subscription(user_id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, plan_name, expire_date FROM subs WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result


def format_remaining_time(expire_date_str):
    try:
        expire_date = datetime.strptime(
            expire_date_str,
            "%Y-%m-%d %H:%M:%S"
        )

        now = datetime.now()
        remaining = expire_date - now

        if remaining.total_seconds() <= 0:
            return "❌ Möhleti gutardy"

        total_seconds = int(remaining.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        return f"{days} gün {hours} sagat {minutes} minut"

    except Exception:
        return "Näbelli"


# ----------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "📊 Signals",
                url="https://t.me/meta5signals_XAUUSD"
            ),
            InlineKeyboardButton(
                "🗞️ News",
                url="https://t.me/GoldFnews"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Chat group",
                url="https://t.me/meta5signal_chat"
            ),
            InlineKeyboardButton(
                "🌐 Website",
                callback_data="results"
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Premium Agzalyk",
                callback_data="premium"
            )
        ],
        [
            InlineKeyboardButton(
                "👤 Meniň profilim",
                callback_data="my_profile"
            )
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
        [
            InlineKeyboardButton(
                "🔙 Yza",
                callback_data="back_to_start"
            )
        ]
    ])


    # ----------------------------------
    # BAŞ MENÝU
    # ----------------------------------

    if query.data == "back_to_start":

        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 Signals",
                    url="https://t.me/meta5signals_XAUUSD"
                ),
                InlineKeyboardButton(
                    "🗞️ News",
                    url="https://t.me/GoldFnews"
                )
            ],
            [
                InlineKeyboardButton(
                    "👥 Chat group",
                    url="https://t.me/meta5signal_chat"
                ),
                InlineKeyboardButton(
                    "🌐 Website",
                    callback_data="results"
                )
            ],
            [
                InlineKeyboardButton(
                    "💎 Premium Agzalyk",
                    callback_data="premium"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 Meniň profilim",
                    callback_data="my_profile"
                )
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


    # ----------------------------------
    # MENIŇ PROFILIM
    # ----------------------------------

    elif query.data == "my_profile":

        user = query.from_user
        user_id = user.id

        username = f"@{user.username}" if user.username else "Ýok"
        full_name = user.full_name

        subscription = get_subscription(user_id)

        if subscription:

            db_username, plan_name, expire_date = subscription

            # REFERAL PREMIUM

            if plan_name == "Referal (Wagtsyz)":

                profile_text = (
                    "👤 **MENIŇ PROFILIŇ**\n\n"
                    f"👨‍💼 Adyňyz: **{full_name}**\n"
                    f"🔗 Username: **{username}**\n"
                    f"🆔 Telegram ID: `{user_id}`\n\n"
                    "💎 **Premium status:** ✅ Aktiw\n"
                    "📦 Plan: **Referal Premium**\n"
                    "♾️ Möhleti: **Wagtsyz**\n"
                    "⏳ Galan wagt: **Wagtsyz**"
                )

            # ADATY PREMIUM

            else:

                remaining = format_remaining_time(expire_date)

                try:
                    expire_datetime = datetime.strptime(
                        expire_date,
                        "%Y-%m-%d %H:%M:%S"
                    )

                    formatted_expire = expire_datetime.strftime(
                        "%d.%m.%Y %H:%M"
                    )

                except Exception:
                    formatted_expire = expire_date

                profile_text = (
                    "👤 **MENIŇ PROFILIŇ**\n\n"
                    f"👨‍💼 Adyňyz: **{full_name}**\n"
                    f"🔗 Username: **{username}**\n"
                    f"🆔 Telegram ID: `{user_id}`\n\n"
                    "💎 **Premium status:** ✅ Aktiw\n"
                    f"📦 Plan: **{plan_name}**\n"
                    f"📅 Gutaryş senesi: **{formatted_expire}**\n"
                    f"⏳ Galan wagt: **{remaining}**"
                )

        else:

            profile_text = (
                "👤 **MENIŇ PROFILIŇ**\n\n"
                f"👨‍💼 Adyňyz: **{full_name}**\n"
                f"🔗 Username: **{username}**\n"
                f"🆔 Telegram ID: `{user_id}`\n\n"
                "💎 **Premium status:** ❌ Aktiw däl\n"
                "📦 Plan: **Premium ýok**\n\n"
                "Premium almak üçin aşakdaky düwmä basyň."
            )


        profile_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "💎 Premium almak",
                    callback_data="premium"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Yza",
                    callback_data="back_to_start"
                )
            ]
        ])

        await query.edit_message_text(
            text=profile_text,
            reply_markup=profile_keyboard,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # WEBSITE
    # ----------------------------------

    if query.data == "results":

        text = "🌐 Website\n\nHäzirlikçe el ýeterli däl."

        await query.edit_message_text(
            text,
            reply_markup=back_keyboard
        )


    # ----------------------------------
    # PREMIUM
    # ----------------------------------

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
            [
                InlineKeyboardButton(
                    "🤝 Meniň referalym bol",
                    callback_data="ref_method"
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 Satyn al",
                    callback_data="buy_method"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Yza",
                    callback_data="back_to_start"
                )
            ]
        ])

        await query.edit_message_text(
            text=text,
            reply_markup=premium_keyboard,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # REFERAL
    # ----------------------------------

    elif query.data == "ref_method":

        text = (
            "🤝 **Referal arkaly Premium almak:**\n\n"
            "1. Aşakdaky düwme arkaly görkezme toparyna girip hasap açyň.\n"
            "2. Depozit goýanyňyzdan soň, **Broker ID nomeriňizi** ýa-da hasabdaky **poçtaňyzy** şu çata hat arkaly iberiň."
        )

        ref_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🤔 Nädip referalyň bolmaly!?",
                    url=TUTORIAL_GROUP_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    "📥 Broker ID iber",
                    callback_data="send_id_prompt"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Yza",
                    callback_data="premium"
                )
            ]
        ])

        await query.edit_message_text(
            text=text,
            reply_markup=ref_keyboard,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # BROKER ID
    # ----------------------------------

    elif query.data == "send_id_prompt":

        context.user_data["waiting_for_type"] = "broker_id"

        text = (
            "Ýaxşy! Indi brokerde açan **ID nomeriňizi** "
            "ýa-da **hasaba bagly poçtaňyzy** şu çata hat arkaly ýazyp iberiň:"
        )

        await query.edit_message_text(
            text,
            reply_markup=back_keyboard
        )

        return


    # ----------------------------------
    # SATYN ALMAK
    # ----------------------------------

    elif query.data == "buy_method":

        text = "💳 **Satyn almak üçin möhleti saýlaň:**"

        buy_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "1 Aýlyk",
                    callback_data="plan_30"
                )
            ],
            [
                InlineKeyboardButton(
                    "3 Aýlyk",
                    callback_data="plan_90"
                )
            ],
            [
                InlineKeyboardButton(
                    "6 Aýlyk",
                    callback_data="plan_180"
                )
            ],
            [
                InlineKeyboardButton(
                    "1 Ýyllyk",
                    callback_data="plan_365"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Yza",
                    callback_data="premium"
                )
            ]
        ])

        await query.edit_message_text(
            text=text,
            reply_markup=buy_keyboard,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # PLANLAR
    # ----------------------------------

    elif query.data.startswith("plan_"):

        days = query.data.split("_")[1]

        prices = {
            "30": "40",
            "90": "100",
            "180": "180",
            "365": "300"
        }

        price = prices.get(days, "40")

        month_label = {
            "30": "bir aýlyk",
            "90": "üç aýlyk",
            "180": "alty aýlyk",
            "365": "bir ýyllyk"
        }.get(days, "bir aýlyk")

        context.user_data["waiting_for_type"] = f"payment_{days}"

        text = (
            f"Siz {month_label} premium satyn alýarsyňyz!\n\n"
            f"Bahasy: 💲{price}\n"
            f"Töleg salgysy: 📌 USDT-TRC20\n"
            f"Töleg kody: 🔑 `TXx9GWMG3JZ7NqEz76f7cXSbr4TFFjbNZx`\n\n"
            "Tölegi doly tamamlanyňyzdan soň töleg edenligiňiz barada "
            "skrinşody hem-de UID kodyňyzy şu çata ýazyň."
        )

        plan_back = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 Yza",
                    callback_data="buy_method"
                )
            ]
        ])

        await query.edit_message_text(
            text=text,
            reply_markup=plan_back,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # ADMIN TASSYKLAMA
    # ----------------------------------

    elif query.data.startswith("approve_"):

        if query.from_user.id != ADMIN_ID:

            await query.answer(
                "Bu düwmäni diňe admin basyp biler!",
                show_alert=True
            )

            return

        parts = query.data.split("_")
        target_user_id = int(parts[1])

        if len(parts) > 2 and parts[2] != "ref":

            days = int(parts[2])

            add_subscription(
                target_user_id,
                "Unknown",
                days
            )

            success_msg = (
                f"✅ Ulanyjy (ID: `{target_user_id}`) "
                f"tassyksyny aldy we {days} günlük premium berildi."
            )

        else:

            add_subscription(
                target_user_id,
                "Unknown",
                0
            )

            success_msg = (
                f"✅ Referal ulanyjy (ID: `{target_user_id}`) "
                "tassyksyny aldy (Wagtsyz)."
            )

        try:

            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "🎉 Gutlaýarys! Siziň maglumatyňyz tassyksyny tapdy. "
                    "Premium toparyň ssylkasy:\n\n"
                    f"{PREMIUM_GROUP_LINK}"
                )
            )

            await query.edit_message_text(
                text=success_msg,
                parse_mode="Markdown"
            )

        except Exception:

            await query.edit_message_text(
                text="⚠️ Ulanyja habar ýetirip bolmady "
                     "(boti bloklan bolmagy mümkin)."
            )

        return


    # ----------------------------------
    # ADMIN RET ETME
    # ----------------------------------

    elif query.data.startswith("reject_"):

        if query.from_user.id != ADMIN_ID:

            await query.answer(
                "Bu düwmäni diňe admin basyp biler!",
                show_alert=True
            )

            return

        target_user_id = int(query.data.split("_")[1])

        try:

            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "❌ Bagyşlaň, siz iberen maglumat ýa-da skrinşod "
                    "tassyklanmadi. Ýalňyşlyk bar bolsa gaýtadan barlaň."
                )
            )

            await query.edit_message_text(
                text=(
                    f"❌ Ulanyjy (ID: `{target_user_id}`) "
                    "üçin sorag rad edildi."
                ),
                parse_mode="Markdown"
            )

        except Exception:

            await query.edit_message_text(
                text="⚠️ Ulanyja habar ýetirip bolmady."
            )

        return


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Ýok"

    waiting_type = context.user_data.get("waiting_for_type")

    if not waiting_type:
        return


    # ----------------------------------
    # REFERAL BROKER ID
    # ----------------------------------

    if waiting_type == "broker_id":

        context.user_data["waiting_for_type"] = None

        text = update.message.text or "Surat ýa-da maglumat"

        admin_text = (
            f"🔔 **Täze Referal Broker Barlag Soragy!**\n\n"
            f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
            f"📋 Broker ID / Poçta: `{text}`"
        )

        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Tassykla",
                    callback_data=f"approve_{user_id}_ref"
                ),
                InlineKeyboardButton(
                    "❌ Rad Et",
                    callback_data=f"reject_{user_id}"
                )
            ]
        ])

        try:

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
                reply_markup=admin_keyboard,
                parse_mode="Markdown"
            )

            await update.message.reply_text(
                "✅ Maglumatyňyz admina iberildi! "
                "Barlanylandan soň premium gruppanyň ssylkasy size iberiler."
            )

        except Exception:

            await update.message.reply_text(
                "⚠️ Ýalňyşlyk ýüze çykdy, "
                "admin ID-niň dogrulygyny barlaň."
            )


    # ----------------------------------
    # TÖLEG
    # ----------------------------------

    elif waiting_type.startswith("payment_"):

        days = waiting_type.split("_")[1]

        context.user_data["waiting_for_type"] = None

        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Tassykla we Ssylka Iber",
                    callback_data=f"approve_{user_id}_{days}"
                ),
                InlineKeyboardButton(
                    "❌ Rad Et",
                    callback_data=f"reject_{user_id}"
                )
            ]
        ])

        try:

            if update.message.photo:

                photo_file_id = update.message.photo[-1].file_id

                caption = (
                    f"💳 **Täze Töleg Skrinşody!** "
                    f"({days} günlük paket)\n\n"
                    f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
                    f"💬 Goşmaça: {update.message.caption or 'Ýok'}"
                )

                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo_file_id,
                    caption=caption,
                    reply_markup=admin_keyboard,
                    parse_mode="Markdown"
                )

            else:

                text_content = update.message.text or "Maglumat ýok"

                admin_text = (
                    f"💳 **Täze Töleg Maglumaty!** "
                    f"({days} günlük paket)\n\n"
                    f"👤 Ulanyjy: @{username} (ID: `{user_id}`)\n"
                    f"📋 UID / Maglumat: `{text_content}`"
                )

                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_text,
                    reply_markup=admin_keyboard,
                    parse_mode="Markdown"
                )

            await update.message.reply_text(
                "✅ Skrinşodyňyz we maglumatyňyz admina iberildi! "
                "Tassyklanandan soň size habar berler."
            )

        except Exception:

            await update.message.reply_text(
                "⚠️ Maglumaty admina ugratmakda "
                "ýalňyşlyk ýüze çykdy."
            )


# ----------------------------------
# PREMIUM MÖHLETINI BARLAMAK
# ----------------------------------

async def check_subscriptions_loop(application):

    while True:

        await asyncio.sleep(3600)

        expired_users = get_expired_users()

        for user_id in expired_users:

            if PREMIUM_GROUP_CHAT_ID:

                try:

                    await application.bot.ban_chat_member(
                        chat_id=PREMIUM_GROUP_CHAT_ID,
                        user_id=user_id
                    )

                    await application.bot.unban_chat_member(
                        chat_id=PREMIUM_GROUP_CHAT_ID,
                        user_id=user_id
                    )

                except Exception:
                    pass

            try:

                await application.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "⚠️ Siziň premium agzalyk möhletiniz gutardy! "
                        "Täzeden agza bolmak üçin /start düwmesine basyň."
                    )
                )

            except Exception:
                pass

            remove_expired_user_from_db(user_id)


def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN tapylmady!")

    init_db()

    Thread(
        target=run_web,
        daemon=True
    ).start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(buttons)
    )

    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            handle_message
        )
    )

    async def post_init(app_instance):

        asyncio.create_task(
            check_subscriptions_loop(app_instance)
        )

    application.post_init = post_init

    print("Meta5Signals Bot started successfully!")

    application.run_polling()


if __name__ == "__main__":
    main()
