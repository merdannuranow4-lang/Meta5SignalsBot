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

# Premium gruppanyň gizlin ssylkasy we Chat ID-si
PREMIUM_GROUP_LINK = "https://t.me/+ydp8yB7HNgNkNzJi"
PREMIUM_GROUP_CHAT_ID = -1004401546667

app = Flask(__name__)

@app.route("/")
def home():
    return "Meta5Signals Bot is running! 🚀"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- DILLER WE TÄKLIPLER (DICTIONARY) ---
LANGS = {
    "tk": {
        "welcome": "🚀 FX_Nexor Bot-a hoş geldiňiz!\n\n💎 Forex & XAUUSD Signals and News\n📈 Professional Market Analysis\n🔔 Real-Time Trading Signals\n\nDili saýlaň / Choose language:",
        "menu_signals": "📊 Signallar",
        "menu_news": "🗞️ Habarlar",
        "menu_chat": "👥 Çat topary",
        "menu_website": "🌐 Web-sahypa",
        "menu_premium": "💎 Premium Agzalyk",
        "menu_profile": "👤 Profilim",
        "menu_lang": "🌐 Dil / Language",
        "back": "🔙 Yza",
        "profile_title": "👤 **Siziň Profilňiz:**\n\n🆔 Telegram ID: `{user_id}`\n👤 Adyňyz: `{username}`\n💎 Status: **{status}**\n⏳ Galan wagt: **{time_left}**",
        "not_vip": "VIP däl (Abonement ýok)",
        "vip_active": "VIP Agza ✅",
        "vip_unlimited": "Wagtsyz (Referal) ♾️",
        "select_lang": "Dil düzüldy: Türkmençe 🇹🇲",
        "premium_desc": "💎 **Eger siz premium agza bolanyňyzda:**\n\n• Signallar - günde 5 den 10 na çenli signal alarsyňyz.\n• Bazara we kriptowalýuta täsir edip biljek habarlar ýetiriler.\n• Risk menejment hasaplanar.\n• Wideojaňda real time söwda ederis.\n• Her hepdäniň soňunda netije.\n\nÖzüñize amatly bolan usuly saýlaň:",
        "ref_btn": "🤝 Meniň referalym bol",
        "buy_btn": "💳 Satyn al",
        "ref_text": "🤝 **Referal arkaly Premium almak:**\n\n1. Aşakdaky düwme arkaly görkezme toparyna girip hasap açyň.\n2. Depozit goýanyňyzdan soň, **Broker ID nomeriňizi** ýa-da hasabdaky **poçtaňyzy** şu çata hat arkaly iberiň.",
        "ref_tutorial_btn": "🤔 Nädip referalyň bolmaly!?",
        "send_id_btn": "📥 Broker ID iber",
        "id_prompt": "Ýaxşy! Indi brokerde açan **ID nomeriňizi** ýa-da **hasaba bagly poçtaňyzy** şu çata hat arkaly ýazyp iberiň:",
        "buy_title": "💳 **Satyn almak üçin möhleti saýlaň:**",
        "admin_approve_success": "✅ Ulanyjy (ID: `{target_user_id}`) tassyksyny aldy we {days} günlük premium berildi.",
        "admin_approve_ref": "✅ Referal ulanyjy (ID: `{target_user_id}`) tassyksyny aldy (Wagtsyz).",
        "user_congrats": "🎉 Gutlaýarys! Siziň maglumatyňyz tassyksyny tapdy. Premium toparyň ssylkasy:\n\n{link}",
        "user_rejected": "❌ Bagyşlaň, siz iberen maglumat ýa-da skrinşod tassyklanmadi.",
        "expired_msg": "⚠️ Siziň premium agzalyk möhletiniz gutardy! Täzeden agza bolmak üçin /start düwmesine basyň."
    },
    "tr": {
        "welcome": "🚀 FX_Nexor Bot'a hoş geldiniz!\n\n💎 Forex & XAUUSD Signals and News\n📈 Professional Market Analysis\n🔔 Real-Time Trading Signals\n\nDil seçin / Choose language:",
        "menu_signals": "📊 Sinyaller",
        "menu_news": "🗞️ Haberler",
        "menu_chat": "👥 Sohbet Grubu",
        "menu_website": "🌐 Web Sitesi",
        "menu_premium": "💎 Premium Üyelik",
        "menu_profile": "👤 Profilim",
        "menu_lang": "🌐 Dil / Language",
        "back": "🔙 Geri",
        "profile_title": "👤 **Profiliniz:**\n\n🆔 Telegram ID: `{user_id}`\n👤 Adınız: `{username}`\n💎 Durum: **{status}**\n⏳ Kalan Süre: **{time_left}**",
        "not_vip": "VIP Değil",
        "vip_active": "VIP Üye ✅",
        "vip_unlimited": "Sınırsız (Referral) ♾️",
        "select_lang": "Dil ayarlandı: Türkçe 🇹🇷",
        "premium_desc": "💎 **Premium üye olduğunuzda:**\n\n• Günde 5-10 sinyal alırsınız.\n• Piyasa ve kripto haberleri iletilir.\n• Risk yönetimi hesaplanır.\n• Canlı yayında işlem yapılır.\n\nLütfen bir yöntem seçin:",
        "ref_btn": "🤝 Referansım Ol",
        "buy_btn": "💳 Satın Al",
        "ref_text": "🤝 **Referans ile Premium Almak:**\n\n1. Eğitim grubuna katılın ve hesap açın.\n2. Broker ID'nizi veya e-postanızı buraya gönderin.",
        "ref_tutorial_btn": "🤔 Nasıl referansım olursun!?",
        "send_id_btn": "📥 Broker ID Gönder",
        "id_prompt": "Harika! Broker ID numaranızı veya e-postanızı buraya yazıp gönderin:",
        "buy_title": "💳 **Satın almak için süre seçin:**",
        "admin_approve_success": "✅ Kullanıcı (ID: `{target_user_id}`) onaylandı ve {days} günlük premium verildi.",
        "admin_approve_ref": "✅ Referans kullanıcı (ID: `{target_user_id}`) onaylandı (Sınırsız).",
        "user_congrats": "🎉 Tebrikler! Bilgileriniz onaylandı. Premium grup bağlantısı:\n\n{link}",
        "user_rejected": "❌ Üzgünüz, gönderdiğiniz bilgiler onaylanmadı.",
        "expired_msg": "⚠️ Premium üyelik süreniz doldu! Yeniden üye olmak için /start tuşuna basın."
    },
    "ru": {
        "welcome": "🚀 Добро пожаловать в FX_Nexor Bot!\n\n💎 Forex & XAUUSD Signals and News\n📈 Professional Market Analysis\n🔔 Real-Time Trading Signals\n\nВыберите язык / Choose language:",
        "menu_signals": "📊 Сигналы",
        "menu_news": "🗞️ Новости",
        "menu_chat": "👥 Чат группа",
        "menu_website": "🌐 Веб-сайт",
        "menu_premium": "💎 Премиум подписка",
        "menu_profile": "👤 Мой профиль",
        "menu_lang": "🌐 Язык / Language",
        "back": "🔙 Назад",
        "profile_title": "👤 **Ваш профиль:**\n\n🆔 Telegram ID: `{user_id}`\n👤 Имя: `{username}`\n💎 Статус: **{status}**\n⏳ Осталось времени: **{time_left}**",
        "not_vip": "Нет подписки",
        "vip_active": "VIP Подписка ✅",
        "vip_unlimited": "Бессрочно (Реферал) ♾️",
        "select_lang": "Язык изменен: Русский 🇷🇺",
        "premium_desc": "💎 **Преимущества премиум подписки:**\n\n• 5-10 сигналов в день.\n• Важные новости рынков.\n• Расчет риск-менеджмента.\n• Торговля в реальном времени.\n\nВыберите способ:",
        "ref_btn": "🤝 Стать рефералом",
        "buy_btn": "💳 Купить",
        "ref_text": "🤝 **Премиум по рефералу:**\n\n1. Откройте счет по ссылке.\n2. Отправьте ваш Broker ID сюда.",
        "ref_tutorial_btn": "🤔 Как это работает!?",
        "send_id_btn": "📥 Отправить Broker ID",
        "id_prompt": "Отлично! Отправьте ваш Broker ID или email:",
        "buy_title": "💳 **Выберите срок подписки:**",
        "admin_approve_success": "✅ Пользователь (ID: `{target_user_id}`) подтвержден, выдано дней: {days}.",
        "admin_approve_ref": "✅ Реферал (ID: `{target_user_id}`) подтвержден (Бессрочно).",
        "user_congrats": "🎉 Поздравляем! Ваша заявка одобрена. Ссылка на премиум группу:\n\n{link}",
        "user_rejected": "❌ К сожалению, ваша заявка была отклонена.",
        "expired_msg": "⚠️ Срок вашей премиум подписки истек! Нажмите /start для продления."
    },
    "en": {
        "welcome": "🚀 Welcome to FX_Nexor Bot!\n\n💎 Forex & XAUUSD Signals and News\n📈 Professional Market Analysis\n🔔 Real-Time Trading Signals\n\nChoose language / Dil seçin:",
        "menu_signals": "📊 Signals",
        "menu_news": "🗞️ News",
        "menu_chat": "👥 Chat group",
        "menu_website": "🌐 Website",
        "menu_premium": "💎 Premium Membership",
        "menu_profile": "👤 My Profile",
        "menu_lang": "🌐 Language",
        "back": "🔙 Back",
        "profile_title": "👤 **Your Profile:**\n\n🆔 Telegram ID: `{user_id}`\n👤 Username: `{username}`\n💎 Status: **{status}**\n⏳ Time left: **{time_left}**",
        "not_vip": "No active VIP",
        "vip_active": "VIP Member ✅",
        "vip_unlimited": "Unlimited (Referral) ♾️",
        "select_lang": "Language set to: English 🇬🇧",
        "premium_desc": "💎 **Premium Benefits:**\n\n• 5-10 signals daily.\n• Market & crypto news.\n• Risk management.\n• Real-time trading sessions.\n\nChoose a method:",
        "ref_btn": "🤝 Become my referral",
        "buy_btn": "💳 Buy subscription",
        "ref_text": "🤝 **Get Premium via Referral:**\n\n1. Open account via instructions.\n2. Send your Broker ID here.",
        "ref_tutorial_btn": "🤔 How to start!?",
        "send_id_btn": "📥 Send Broker ID",
        "id_prompt": "Great! Send your Broker ID or email address here:",
        "buy_title": "💳 **Select subscription period:**",
        "admin_approve_success": "✅ User (ID: `{target_user_id}`) approved for {days} days.",
        "admin_approve_ref": "✅ Referral user (ID: `{target_user_id}`) approved (Unlimited).",
        "user_congrats": "🎉 Congratulations! Your request is approved. Premium group link:\n\n{link}",
        "user_rejected": "❌ Sorry, your submission was rejected.",
        "expired_msg": "⚠️ Your premium subscription has expired! Press /start to renew."
    }
}

# --- BAZA BILEN IŞLEMEK (SQLite) ---
def init_db():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subs (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            plan_name TEXT,
            expire_date TEXT,
            language TEXT DEFAULT 'tk'
        )
    """)
    conn.commit()
    conn.close()

def get_user_lang(user_id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM subs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    return "tk"

def set_user_lang(user_id, username, lang):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO subs (user_id, username, language) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET language = ?
    """, (user_id, username, lang, lang))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT plan_name, expire_date FROM subs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_subscription(user_id, username, days, lang='tk'):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT expire_date, plan_name FROM subs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    now = datetime.now()
    
    if days > 0:
        if row and row[0] and "Wagtsyz" not in str(row[1]):
            try:
                old_expire = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                base_time = old_expire if old_expire > now else now
            except Exception:
                base_time = now
        else:
            base_time = now
            
        expire_date = base_time + timedelta(days=days)
        expire_str = expire_date.strftime("%Y-%m-%d %H:%M:%S")
        plan_text = f"{days} gün"
    else:
        expire_date = now + timedelta(days=3650)
        expire_str = expire_date.strftime("%Y-%m-%d %H:%M:%S")
        plan_text = "Referal (Wagtsyz)"

    cursor.execute("""
        INSERT INTO subs (user_id, username, plan_name, expire_date, language)
        VALUES (?, ?, ?, ?, COALESCE((SELECT language FROM subs WHERE user_id = ?), ?))
        ON CONFLICT(user_id) DO UPDATE SET plan_name = ?, expire_date = ?
    """, (user_id, username, plan_text, expire_str, user_id, lang, plan_text, expire_str))
    conn.commit()
    conn.close()

def get_expired_users():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT user_id FROM subs WHERE expire_date <= ? AND plan_name != 'Referal (Wagtsyz)' AND expire_date IS NOT NULL", (now_str,))
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def remove_expired_user_from_db(user_id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE subs SET plan_name = NULL, expire_date = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# ----------------------------------

def get_main_keyboard(lang):
    t = LANGS.get(lang, LANGS["tk"])
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t["menu_signals"], url="https://t.me/meta5signals_XAUUSD"),
            InlineKeyboardButton(t["menu_news"], url="https://t.me/GoldFnews")
        ],
        [
            InlineKeyboardButton(t["menu_chat"], url="https://t.me/meta5signal_chat"),
            InlineKeyboardButton(t["menu_website"], callback_data="results")
        ],
        [
            InlineKeyboardButton(t["menu_profile"], callback_data="my_profile"),
            InlineKeyboardButton(t["menu_premium"], callback_data="premium")
        ],
        [
            InlineKeyboardButton(t["menu_lang"], callback_data="change_lang")
        ]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    lang = get_user_lang(user.id)
    t = LANGS.get(lang, LANGS["tk"])
    
    await update.message.reply_text(
        t["welcome"],
        reply_markup=get_main_keyboard(lang)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or "Ýok"
    lang = get_user_lang(user_id)
    t = LANGS.get(lang, LANGS["tk"])

    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t["back"], callback_data="back_to_start")]
    ])

    if query.data == "back_to_start":
        await query.edit_message_text(
            text=t["welcome"],
            reply_markup=get_main_keyboard(lang),
            parse_mode="Markdown"
        )
        return

    # Dil üýtgetmek menýusy
    elif query.data == "change_lang":
        lang_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="set_lang_tk"),
                InlineKeyboardButton("🇹🇷 Türkçe", callback_data="set_lang_tr")
            ],
            [
                InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
                InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
            ],
            [InlineKeyboardButton(t["back"], callback_data="back_to_start")]
        ])
        await query.edit_message_text("Dil saýlaň / Choose language:", reply_markup=lang_keyboard)
        return

    elif query.data.startswith("set_lang_"):
        new_lang = query.data.split("_")[2]
        set_user_lang(user_id, username, new_lang)
        new_t = LANGS.get(new_lang, LANGS["tk"])
        await query.edit_message_text(
            text=new_t["select_lang"],
            reply_markup=get_main_keyboard(new_lang)
        )
        return

    # Profil barlamak
    elif query.data == "my_profile":
        info = get_user_info(user_id)
        status_text = t["not_vip"]
        time_left_text = "-"

        if info and info[0]:
            plan_name, expire_str = info
            if "Wagtsyz" in plan_name:
                status_text = t["vip_unlimited"]
                time_left_text = "♾️"
            elif expire_str:
                try:
                    exp_dt = datetime.strptime(expire_str, "%Y-%m-%d %H:%M:%S")
                    now_dt = datetime.now()
                    if exp_dt > now_dt:
                        diff = exp_dt - now_dt
                        days = diff.days
                        hours = diff.seconds // 3600
                        status_text = t["vip_active"]
                        time_left_text = f"{days} gün {hours} sagat"
                    else:
                        status_text = t["not_vip"]
                except Exception:
                    status_text = t["vip_active"]

        profile_msg = t["profile_title"].format(
            user_id=user_id,
            username=username,
            status=status_text,
            time_left=time_left_text
        )
        await query.edit_message_text(text=profile_msg, reply_markup=back_keyboard, parse_mode="Markdown")
        return

    elif query.data == "results":
        text = f"🌐 Website\n\nHäzirlikçe el ýeterli däl." if lang == "tk" else f"🌐 Website\n\nŞu an erişilebilir değil." if lang == "tr" else f"🌐 Веб-сайт\n\nПока недоступен." if lang == "ru" else f"🌐 Website\n\nCurrently unavailable."
        await query.edit_message_text(text, reply_markup=back_keyboard)
    
    elif query.data == "premium":
        premium_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t["ref_btn"], callback_data="ref_method")],
            [InlineKeyboardButton(t["buy_btn"], callback_data="buy_method")],
            [InlineKeyboardButton(t["back"], callback_data="back_to_start")]
        ])
        await query.edit_message_text(text=t["premium_desc"], reply_markup=premium_keyboard, parse_mode="Markdown")
        return

    elif query.data == "ref_method":
        ref_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t["ref_tutorial_btn"], url=TUTORIAL_GROUP_LINK)],
            [InlineKeyboardButton(t["send_id_btn"], callback_data="send_id_prompt")],
            [InlineKeyboardButton(t["back"], callback_data="premium")]
        ])
        await query.edit_message_text(text=t["ref_text"], reply_markup=ref_keyboard, parse_mode="Markdown")
        return

    elif query.data == "send_id_prompt":
        context.user_data["waiting_for_type"] = "broker_id"
        await query.edit_message_text(text=t["id_prompt"], reply_markup=back_keyboard, parse_mode="Markdown")
        return

    elif query.data == "buy_method":
        buy_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Aý / Month", callback_data="plan_30")],
            [InlineKeyboardButton("3 Aý / Months", callback_data="plan_90")],
            [InlineKeyboardButton("6 Aý / Months", callback_data="plan_180")],
            [InlineKeyboardButton("1 Ýyl / Year", callback_data="plan_365")],
            [InlineKeyboardButton(t["back"], callback_data="premium")]
        ])
        await query.edit_message_text(text=t["buy_title"], reply_markup=buy_keyboard, parse_mode="Markdown")
        return

    elif query.data.startswith("plan_"):
        days = query.data.split("_")[1]
        prices = {"30": "40", "90": "100", "180": "180", "365": "300"}
        price = prices.get(days, "40")

        context.user_data["waiting_for_type"] = f"payment_{days}"

        text = (
            f"📦 Plan: {days} days\n"
            f"Price: 💲{price}\n"
            f"USDT-TRC20 Address:\n`TXx9GWMG3JZ7NqEz76f7cXSbr4TFFjbNZx`\n\n"
            "Töleg edip bolanyňyzdan soň skrinşody ýa-da UID kodyňyzy iberiň."
        )
        plan_back = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="buy_method")]])
        await query.edit_message_text(text=text, reply_markup=plan_back, parse_mode="Markdown")
        return

    # Admin Tassyklama / Ret etme
    elif query.data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Admin dälsiňiz!", show_alert=True)
            return
        
        parts = query.data.split("_")
        target_user_id = int(parts[1])
        target_lang = get_user_lang(target_user_id)
        target_t = LANGS.get(target_lang, LANGS["tk"])

        if len(parts) > 2 and parts[2] != "ref":
            days = int(parts[2])
            add_subscription(target_user_id, "Unknown", days, target_lang)
            success_msg = target_t["admin_approve_success"].format(target_user_id=target_user_id, days=days)
        else:
            add_subscription(target_user_id, "Unknown", 0, target_lang)
            success_msg = target_t["admin_approve_ref"].format(target_user_id=target_user_id)

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=target_t["user_congrats"].format(link=PREMIUM_GROUP_LINK)
            )
            await query.edit_message_text(text=success_msg, parse_mode="Markdown")
        except Exception:
            await query.edit_message_text(text="⚠️ Ulanyja habar ýetirip bolmady.")
        return

    elif query.data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Admin dälsiňiz!", show_alert=True)
            return
        
        target_user_id = int(query.data.split("_")[1])
        target_lang = get_user_lang(target_user_id)
        target_t = LANGS.get(target_lang, LANGS["tk"])

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=target_t["user_rejected"]
            )
            await query.edit_message_text(text=f"❌ Ulanyjy (ID: `{target_user_id}`) rad edildi.")
        except Exception:
            await query.edit_message_text(text="⚠️ Ulanyja habar ýetirip bolmady.")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Ýok"
    waiting_type = context.user_data.get("waiting_for_type")
    lang = get_user_lang(user_id)
    t = LANGS.get(lang, LANGS["tk"])

    if not waiting_type:
        return

    if waiting_type == "broker_id":
        context.user_data["waiting_for_type"] = None
        text = update.message.text or "Surat"
        
        admin_text = f"🔔 **Referal Soragy!**\n\n👤 Ulanyjy: @{username} (ID: `{user_id}`)\n📋 Broker ID: `{text}`"
        admin_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Tassykla", callback_data=f"approve_{user_id}_ref"), InlineKeyboardButton("❌ Rad Et", callback_data=f"reject_{user_id}")]
        ])
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
            await update.message.reply_text("✅ Maglumatyňyz admina iberildi!")
        except Exception:
            await update.message.reply_text("⚠️ Ýalňyşlyk ýüze çykdy.")

    elif waiting_type.startswith("payment_"):
        days = waiting_type.split("_")[1]
        context.user_data["waiting_for_type"] = None
        
        admin_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Tassykla", callback_data=f"approve_{user_id}_{days}"), InlineKeyboardButton("❌ Rad Et", callback_data=f"reject_{user_id}")]
        ])

        try:
            if update.message.photo:
                photo_file_id = update.message.photo[-1].file_id
                caption = f"💳 **Töleg Skrinşody!** ({days} gün)\n\n👤 @{username} (ID: `{user_id}`)"
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=caption, reply_markup=admin_keyboard, parse_mode="Markdown")
            else:
                text_content = update.message.text or "Maglumat"
                admin_text = f"💳 **Töleg Maglumaty!** ({days} gün)\n\n👤 @{username} (ID: `{user_id}`)\n📋 {text_content}"
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")

            await update.message.reply_text("✅ Maglumatyňyz admina iberildi!")
        except Exception:
            await update.message.reply_text("⚠️ Ugratmakda ýalňyşlyk.")

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
            
            user_lang = get_user_lang(user_id)
            user_t = LANGS.get(user_lang, LANGS["tk"])
            try:
                await application.bot.send_message(
                    chat_id=user_id,
                    text=user_t["expired_msg"]
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
