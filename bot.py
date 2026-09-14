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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_languages (
            user_id INTEGER PRIMARY KEY,
            language TEXT
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
# DIL SISTEMASY
# ----------------------------------

LANGUAGES = {
    "tk": "🇹🇲 Türkmençe",
    "tr": "🇹🇷 Türkçe",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English"
}


def set_user_language(user_id, language):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO user_languages (user_id, language)
        VALUES (?, ?)
    """, (user_id, language))

    conn.commit()
    conn.close()


def get_user_language(user_id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT language FROM user_languages WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return None


def language_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🇹🇲 Türkmençe",
                callback_data="lang_tk"
            )
        ],
        [
            InlineKeyboardButton(
                "🇹🇷 Türkçe",
                callback_data="lang_tr"
            )
        ],
        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="lang_ru"
            )
        ],
        [
            InlineKeyboardButton(
                "🇬🇧 English",
                callback_data="lang_en"
            )
        ]
    ])


# ----------------------------------
# TERJIME SISTEMASY
# ----------------------------------

TEXTS = {

    "tk": {
        "welcome": (
            "🚀 FX_Nexor Bot-a hoş geldiňiz!\n\n"
            "💎 Forex & XAUUSD Signals and News\n"
            "📈 Professional Market Analysis\n"
            "🔔 Real-Time Trading Signals\n\n"
            "Aşakdaky menýudan saýla:"
        ),

        "signals": "📊 Signals",
        "news": "🗞️ News",
        "chat_group": "👥 Chat group",
        "website": "🌐 Website",
        "premium_membership": "💎 Premium Agzalyk",
        "my_profile": "👤 Meniň profilim",
        "language": "🌐 Dil",

        "website_text": "🌐 Website\n\nHäzirlikçe el ýeterli däl.",

        "premium_text": (
            "💎 **Eger siz premium agza bolanyňyzda:**\n\n"
            "• Signallar - günde 5 den 10 na çenli signal alarsyňyz.\n\n"
            "• Bazara we kriptowalýuta täsir edip biljek habarlar ýetiriler.\n\n"
            "• Risk menejment hasaplanar.\n\n"
            "• Wideojaňda real time söwda ederis.\n\n"
            "• Her hepdäniň soňunda netije ýagny gazanalynan we ýitirlen pipsler hasaplanar.\n\n"
            "Özüñize amatly bolan usuly saýlaň:"
        ),

        "ref_method": "🤝 Meniň referalym bol",
        "buy": "💳 Satyn al",
        "back": "🔙 Yza",

        "ref_text": (
            "🤝 **Referal arkaly Premium almak:**\n\n"
            "1. Aşakdaky düwme arkaly görkezme toparyna girip hasap açyň.\n"
            "2. Depozit goýanyňyzdan soň, **Broker ID nomeriňizi** ýa-da hasabdaky **poçtaňyzy** şu çata hat arkaly iberiň."
        ),

        "tutorial": "🤔 Nädip referalyň bolmaly!?",
        "send_id": "📥 Broker ID iber",

        "send_id_text": (
            "Ýaxşy! Indi brokerde açan **ID nomeriňizi** "
            "ýa-da **hasaba bagly poçtaňyzy** şu çata hat arkaly ýazyp iberiň:"
        ),

        "buy_text": "💳 **Satyn almak üçin möhleti saýlaň:**",

        "one_month": "1 Aýlyk",
        "three_month": "3 Aýlyk",
        "six_month": "6 Aýlyk",
        "one_year": "1 Ýyllyk",

        "payment_text": (
            "Siz {month_label} premium satyn alýarsyňyz!\n\n"
            "Bahasy: 💲{price}\n"
            "Töleg salgysy: 📌 USDT-TRC20\n"
            "Töleg kody: 🔑 `TXx9GWMG3JZ7NqEz76f7cXSbr4TFFjbNZx`\n\n"
            "Tölegi doly tamamlanyňyzdan soň töleg edenligiňiz barada "
            "skrinşody hem-de UID kodyňyzy şu çata ýazyň."
        ),

        "profile_title": "👤 **MENIŇ PROFILIŇ**",
        "name": "👨‍💼 Adyňyz",
        "username": "🔗 Username",
        "telegram_id": "🆔 Telegram ID",
        "premium_status": "💎 **Premium status:**",
        "active": "✅ Aktiw",
        "inactive": "❌ Aktiw däl",
        "plan": "📦 Plan",
        "referral_premium": "Referal Premium",
        "unlimited": "Wagtsyz",
        "remaining": "⏳ Galan wagt",
        "expiry": "📅 Gutaryş senesi",
        "no_premium": "Premium ýok",
        "premium_get": "Premium almak üçin aşakdaky düwmä basyň.",
        "get_premium": "💎 Premium almak",

        "expired": "❌ Möhleti gutardy",
        "unknown": "Näbelli",

        "sent_admin": (
            "✅ Maglumatyňyz admina iberildi! "
            "Barlanylandan soň premium gruppanyň ssylkasy size iberiler."
        ),

        "admin_error": (
            "⚠️ Ýalňyşlyk ýüze çykdy, "
            "admin ID-niň dogrulygyny barlaň."
        ),

        "payment_sent": (
            "✅ Skrinşodyňyz we maglumatyňyz admina iberildi! "
            "Tassyklanandan soň size habar berler."
        ),

        "payment_error": (
            "⚠️ Maglumaty admina ugratmakda "
            "ýalňyşlyk ýüze çykdy."
        ),

        "approved": (
            "🎉 Gutlaýarys! Siziň maglumatyňyz tassyksyny tapdy. "
            "Premium toparyň ssylkasy:\n\n"
            "{link}"
        ),

        "expired_message": (
            "⚠️ Siziň premium agzalyk möhletiniz gutardy! "
            "Täzeden agza bolmak üçin /start düwmesine basyň."
        ),

        "rejected": (
            "❌ Bagyşlaň, siz iberen maglumat ýa-da skrinşod "
            "tassyklanmadi. Ýalňyşlyk bar bolsa gaýtadan barlaň."
        ),

        "language_selected": "✅ Dil üýtgedildi.",
        "choose_language": "🌐 Dili saýlaň:"
    },


    "tr": {
        "welcome": (
            "🚀 FX_Nexor Bot'a hoş geldiniz!\n\n"
            "💎 Forex & XAUUSD Sinyalleri ve Haberleri\n"
            "📈 Profesyonel Piyasa Analizi\n"
            "🔔 Gerçek Zamanlı İşlem Sinyalleri\n\n"
            "Aşağıdaki menüden seçim yapın:"
        ),

        "signals": "📊 Sinyaller",
        "news": "🗞️ Haberler",
        "chat_group": "👥 Sohbet grubu",
        "website": "🌐 Web sitesi",
        "premium_membership": "💎 Premium Üyelik",
        "my_profile": "👤 Profilim",
        "language": "🌐 Dil",

        "website_text": "🌐 Web sitesi\n\nŞimdilik kullanılamıyor.",

        "premium_text": (
            "💎 **Premium üye olduğunuzda:**\n\n"
            "• Günde 5 ila 10 sinyal alırsınız.\n\n"
            "• Piyasayı ve kripto para piyasasını etkileyebilecek haberler paylaşılır.\n\n"
            "• Risk yönetimi hesaplanır.\n\n"
            "• Görüntülü görüşmede gerçek zamanlı işlem yaparız.\n\n"
            "• Her hafta sonunda kazanılan ve kaybedilen pipler hesaplanır.\n\n"
            "Size uygun yöntemi seçin:"
        ),

        "ref_method": "🤝 Referansım olun",
        "buy": "💳 Satın al",
        "back": "🔙 Geri",

        "ref_text": (
            "🤝 **Referans yoluyla Premium alma:**\n\n"
            "1. Aşağıdaki butondan rehber grubuna girip hesap açın.\n"
            "2. Depozito yatırdıktan sonra **Broker ID numaranızı** veya hesabınızdaki **e-posta adresinizi** bu sohbete gönderin."
        ),

        "tutorial": "🤔 Nasıl referans olunur!?",
        "send_id": "📥 Broker ID gönder",

        "send_id_text": (
            "Tamam! Şimdi brokerde açtığınız **ID numaranızı** "
            "veya **hesabınıza bağlı e-posta adresinizi** bu sohbete gönderin:"
        ),

        "buy_text": "💳 **Satın almak için süreyi seçin:**",

        "one_month": "1 Aylık",
        "three_month": "3 Aylık",
        "six_month": "6 Aylık",
        "one_year": "1 Yıllık",

        "payment_text": (
            "{month_label} premium satın alıyorsunuz!\n\n"
            "Fiyat: 💲{price}\n"
            "Ödeme adresi: 📌 USDT-TRC20\n"
            "Ödeme adresi: 🔑 `TXx9GWMG3JZ7NqEz76f7cXSbr4TFFjbNZx`\n\n"
            "Ödemeyi tamamladıktan sonra ödeme ekran görüntüsünü "
            "ve UID kodunuzu bu sohbete gönderin."
        ),

        "profile_title": "👤 **PROFİLİM**",
        "name": "👨‍💼 Adınız",
        "username": "🔗 Kullanıcı adı",
        "telegram_id": "🆔 Telegram ID",
        "premium_status": "💎 **Premium durumu:**",
        "active": "✅ Aktif",
        "inactive": "❌ Aktif değil",
        "plan": "📦 Plan",
        "referral_premium": "Referans Premium",
        "unlimited": "Sınırsız",
        "remaining": "⏳ Kalan süre",
        "expiry": "📅 Bitiş tarihi",
        "no_premium": "Premium yok",
        "premium_get": "Premium almak için aşağıdaki butona basın.",
        "get_premium": "💎 Premium al",

        "expired": "❌ Süresi doldu",
        "unknown": "Bilinmiyor",

        "sent_admin": (
            "✅ Bilgileriniz admin'e gönderildi! "
            "Kontrol edildikten sonra premium grup bağlantısı size gönderilecektir."
        ),

        "admin_error": (
            "⚠️ Bir hata oluştu, "
            "admin ID'sini kontrol edin."
        ),

        "payment_sent": (
            "✅ Ekran görüntünüz ve bilgileriniz admin'e gönderildi! "
            "Onaylandıktan sonra size haber verilecektir."
        ),

        "payment_error": (
            "⚠️ Bilgilerin admin'e gönderilmesi sırasında "
            "bir hata oluştu."
        ),

        "approved": (
            "🎉 Tebrikler! Bilgileriniz onaylandı. "
            "Premium grup bağlantısı:\n\n"
            "{link}"
        ),

        "expired_message": (
            "⚠️ Premium üyelik süreniz doldu! "
            "Tekrar üye olmak için /start butonuna basın."
        ),

        "rejected": (
            "❌ Üzgünüz, gönderdiğiniz bilgi veya ekran görüntüsü "
            "onaylanmadı. Bir hata varsa lütfen tekrar kontrol edin."
        ),

        "language_selected": "✅ Dil değiştirildi.",
        "choose_language": "🌐 Dil seçin:"
    },


    "ru": {
        "welcome": (
            "🚀 Добро пожаловать в FX_Nexor Bot!\n\n"
            "💎 Forex & XAUUSD Сигналы и Новости\n"
            "📈 Профессиональный анализ рынка\n"
            "🔔 Торговые сигналы в реальном времени\n\n"
            "Выберите пункт меню ниже:"
        ),

        "signals": "📊 Сигналы",
        "news": "🗞️ Новости",
        "chat_group": "👥 Чат-группа",
        "website": "🌐 Веб-сайт",
        "premium_membership": "💎 Premium подписка",
        "my_profile": "👤 Мой профиль",
        "language": "🌐 Язык",

        "website_text": "🌐 Веб-сайт\n\nВ данный момент недоступен.",

        "premium_text": (
            "💎 **Став Premium участником, вы получите:**\n\n"
            "• От 5 до 10 сигналов в день.\n\n"
            "• Новости, которые могут повлиять на рынок и криптовалюты.\n\n"
            "• Расчёт риск-менеджмента.\n\n"
            "• Торговлю в реальном времени во время видеозвонка.\n\n"
            "• В конце каждой недели подсчёт заработанных и потерянных пипсов.\n\n"
            "Выберите удобный способ:"
        ),

        "ref_method": "🤝 Стать моим рефералом",
        "buy": "💳 Купить",
        "back": "🔙 Назад",

        "ref_text": (
            "🤝 **Получение Premium через реферал:**\n\n"
            "1. Перейдите в группу инструкций через кнопку ниже и откройте счёт.\n"
            "2. После внесения депозита отправьте сюда **номер Broker ID** или **электронную почту**, связанную с аккаунтом."
        ),

        "tutorial": "🤔 Как стать рефералом!?",
        "send_id": "📥 Отправить Broker ID",

        "send_id_text": (
            "Хорошо! Теперь отправьте сюда **номер ID**, который вы открыли у брокера, "
            "или **электронную почту, связанную с аккаунтом**:"
        ),

        "buy_text": "💳 **Выберите срок покупки:**",

        "one_month": "1 месяц",
        "three_month": "3 месяца",
        "six_month": "6 месяцев",
        "one_year": "1 год",

        "payment_text": (
            "Вы покупаете {month_label} Premium!\n\n"
            "Цена: 💲{price}\n"
            "Адрес оплаты: 📌 USDT-TRC20\n"
            "Адрес оплаты: 🔑 `TXx9GWMG3JZ7NqEz76f7cXSbr4TFFjbNZx`\n\n"
            "После завершения оплаты отправьте в этот чат "
            "скриншот оплаты и ваш UID-код."
        ),

        "profile_title": "👤 **МОЙ ПРОФИЛЬ**",
        "name": "👨‍💼 Имя",
        "username": "🔗 Имя пользователя",
        "telegram_id": "🆔 Telegram ID",
        "premium_status": "💎 **Статус Premium:**",
        "active": "✅ Активен",
        "inactive": "❌ Не активен",
        "plan": "📦 План",
        "referral_premium": "Реферальный Premium",
        "unlimited": "Бессрочно",
        "remaining": "⏳ Оставшееся время",
        "expiry": "📅 Дата окончания",
        "no_premium": "Premium отсутствует",
        "premium_get": "Чтобы получить Premium, нажмите кнопку ниже.",
        "get_premium": "💎 Получить Premium",

        "expired": "❌ Срок истёк",
        "unknown": "Неизвестно",

        "sent_admin": (
            "✅ Ваша информация отправлена администратору! "
            "После проверки ссылка на Premium-группу будет отправлена вам."
        ),

        "admin_error": (
            "⚠️ Произошла ошибка, "
            "проверьте правильность ID администратора."
        ),

        "payment_sent": (
            "✅ Скриншот и информация отправлены администратору! "
            "После подтверждения вы получите уведомление."
        ),

        "payment_error": (
            "⚠️ Произошла ошибка при отправке "
            "информации администратору."
        ),

        "approved": (
            "🎉 Поздравляем! Ваша информация подтверждена. "
            "Ссылка на Premium-группу:\n\n"
            "{link}"
        ),

        "expired_message": (
            "⚠️ Срок вашей Premium-подписки истёк! "
            "Чтобы снова стать участником, нажмите /start."
        ),

        "rejected": (
            "❌ К сожалению, отправленная вами информация или скриншот "
            "не были подтверждены. Если произошла ошибка, проверьте данные и отправьте снова."
        ),

        "language_selected": "✅ Язык изменён.",
        "choose_language": "🌐 Выберите язык:"
    },


    "en": {
        "welcome": (
            "🚀 Welcome to FX_Nexor Bot!\n\n"
            "💎 Forex & XAUUSD Signals and News\n"
            "📈 Professional Market Analysis\n"
            "🔔 Real-Time Trading Signals\n\n"
            "Choose from the menu below:"
        ),

        "signals": "📊 Signals",
        "news": "🗞️ News",
        "chat_group": "👥 Chat group",
        "website": "🌐 Website",
        "premium_membership": "💎 Premium Membership",
        "my_profile": "👤 My Profile",
        "language": "🌐 Language",

        "website_text": "🌐 Website\n\nCurrently unavailable.",

        "premium_text": (
            "💎 **As a Premium member you will receive:**\n\n"
            "• From 5 to 10 signals per day.\n\n"
            "• News that may affect the market and cryptocurrency.\n\n"
            "• Risk management calculations.\n\n"
            "• Real-time trading during video calls.\n\n"
            "• Weekly calculation of earned and lost pips.\n\n"
            "Choose the option that suits you:"
        ),

        "ref_method": "🤝 Become my referral",
        "buy": "💳 Buy",
        "back": "🔙 Back",

        "ref_text": (
            "🤝 **Get Premium through referral:**\n\n"
            "1. Join the tutorial group using the button below and open an account.\n"
            "2. After making a deposit, send your **Broker ID number** or the **email connected to your account** in this chat."
        ),

        "tutorial": "🤔 How to become a referral!?",
        "send_id": "📥 Send Broker ID",

        "send_id_text": (
            "Okay! Now send the **ID number** you opened with the broker "
            "or the **email connected to your account** in this chat:"
        ),

        "buy_text": "💳 **Choose the subscription period:**",

        "one_month": "1 Month",
        "three_month": "3 Months",
        "six_month": "6 Months",
        "one_year": "1 Year",

        "payment_text": (
            "You are purchasing {month_label} Premium!\n\n"
            "Price: 💲{price}\n"
            "Payment address: 📌 USDT-TRC20\n"
            "Payment address: 🔑 `TXx9GWMG3JZ7NqEz76f7cXSbr4TFFjbNZx`\n\n"
            "After completing the payment, send a screenshot of the payment "
            "and your UID code in this chat."
        ),

        "profile_title": "👤 **MY PROFILE**",
        "name": "👨‍💼 Name",
        "username": "🔗 Username",
        "telegram_id": "🆔 Telegram ID",
        "premium_status": "💎 **Premium status:**",
        "active": "✅ Active",
        "inactive": "❌ Inactive",
        "plan": "📦 Plan",
        "referral_premium": "Referral Premium",
        "unlimited": "Unlimited",
        "remaining": "⏳ Remaining time",
        "expiry": "📅 Expiration date",
        "no_premium": "No Premium",
        "premium_get": "Press the button below to get Premium.",
        "get_premium": "💎 Get Premium",

        "expired": "❌ Expired",
        "unknown": "Unknown",

        "sent_admin": (
            "✅ Your information has been sent to the admin! "
            "After verification, the Premium group link will be sent to you."
        ),

        "admin_error": (
            "⚠️ An error occurred, "
            "please check the admin ID."
        ),

        "payment_sent": (
            "✅ Your screenshot and information have been sent to the admin! "
            "You will be notified after approval."
        ),

        "payment_error": (
            "⚠️ An error occurred while sending "
            "the information to the admin."
        ),

        "approved": (
            "🎉 Congratulations! Your information has been approved. "
            "Premium group link:\n\n"
            "{link}"
        ),

        "expired_message": (
            "⚠️ Your Premium membership has expired! "
            "Press /start to become a member again."
        ),

        "rejected": (
            "❌ Sorry, the information or screenshot you submitted "
            "was not approved. If there is an error, please check and submit again."
        ),

        "language_selected": "✅ Language changed.",
        "choose_language": "🌐 Choose your language:"
    }
}


def t(user_id, key, **kwargs):
    language = get_user_language(user_id) or "tk"

    text = TEXTS.get(language, TEXTS["tk"]).get(
        key,
        TEXTS["tk"].get(key, key)
    )

    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass

    return text


# ----------------------------------
# BAŞ MENÝU
# ----------------------------------

def main_keyboard(user_id):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                t(user_id, "signals"),
                url="https://t.me/meta5signals_XAUUSD"
            ),
            InlineKeyboardButton(
                t(user_id, "news"),
                url="https://t.me/GoldFnews"
            )
        ],
        [
            InlineKeyboardButton(
                t(user_id, "chat_group"),
                url="https://t.me/meta5signal_chat"
            ),
            InlineKeyboardButton(
                t(user_id, "website"),
                callback_data="results"
            )
        ],
        [
            InlineKeyboardButton(
                t(user_id, "premium_membership"),
                callback_data="premium"
            )
        ],
        [
            InlineKeyboardButton(
                t(user_id, "my_profile"),
                callback_data="my_profile"
            )
        ],
        [
            InlineKeyboardButton(
                t(user_id, "language"),
                callback_data="change_language"
            )
        ]
    ])


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


def format_remaining_time(expire_date_str, user_id):
    try:
        expire_date = datetime.strptime(
            expire_date_str,
            "%Y-%m-%d %H:%M:%S"
        )

        now = datetime.now()
        remaining = expire_date - now

        if remaining.total_seconds() <= 0:
            return t(user_id, "expired")

        total_seconds = int(remaining.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        language = get_user_language(user_id) or "tk"

        if language == "tk":
            return f"{days} gün {hours} sagat {minutes} minut"

        elif language == "tr":
            return f"{days} gün {hours} saat {minutes} dakika"

        elif language == "ru":
            return f"{days} дн. {hours} ч. {minutes} мин."

        else:
            return f"{days} days {hours} hours {minutes} minutes"

    except Exception:
        return t(user_id, "unknown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    language = get_user_language(user_id)

    if not language:

        await update.message.reply_text(
            "🌐 Dili saýlaň / Dil seçin / Выберите язык / Choose your language:",
            reply_markup=language_keyboard()
        )

        return

    await update.message.reply_text(
        t(user_id, "welcome"),
        reply_markup=main_keyboard(user_id)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    back_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                t(user_id, "back"),
                callback_data="back_to_start"
            )
        ]
    ])


    # ----------------------------------
    # DIL SAÝLAMAK
    # ----------------------------------

    if query.data == "change_language":

        await query.edit_message_text(
            text=t(user_id, "choose_language"),
            reply_markup=language_keyboard()
        )

        return


    if query.data.startswith("lang_"):

        language = query.data.split("_")[1]

        if language not in LANGUAGES:
            language = "tk"

        set_user_language(user_id, language)

        await query.edit_message_text(
            text=t(user_id, "language_selected"),
            reply_markup=main_keyboard(user_id)
        )

        return


    # ----------------------------------
    # BAŞ MENÝU
    # ----------------------------------

    if query.data == "back_to_start":

        await query.edit_message_text(
            text=t(user_id, "welcome"),
            reply_markup=main_keyboard(user_id)
        )

        return


    # ----------------------------------
    # MENIŇ PROFILIM
    # ----------------------------------

    elif query.data == "my_profile":

        user = query.from_user

        username = f"@{user.username}" if user.username else t(user_id, "unknown")
        full_name = user.full_name

        subscription = get_subscription(user_id)

        if subscription:

            db_username, plan_name, expire_date = subscription

            # REFERAL PREMIUM

            if plan_name == "Referal (Wagtsyz)":

                profile_text = (
                    f"{t(user_id, 'profile_title')}\n\n"
                    f"{t(user_id, 'name')}: **{full_name}**\n"
                    f"{t(user_id, 'username')}: **{username}**\n"
                    f"{t(user_id, 'telegram_id')}: `{user_id}`\n\n"
                    f"{t(user_id, 'premium_status')} {t(user_id, 'active')}\n"
                    f"{t(user_id, 'plan')}: **{t(user_id, 'referral_premium')}**\n"
                    f"♾️ {t(user_id, 'expiry')}: **{t(user_id, 'unlimited')}**\n"
                    f"{t(user_id, 'remaining')}: **{t(user_id, 'unlimited')}**"
                )

            # ADATY PREMIUM

            else:

                remaining = format_remaining_time(
                    expire_date,
                    user_id
                )

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
                    f"{t(user_id, 'profile_title')}\n\n"
                    f"{t(user_id, 'name')}: **{full_name}**\n"
                    f"{t(user_id, 'username')}: **{username}**\n"
                    f"{t(user_id, 'telegram_id')}: `{user_id}`\n\n"
                    f"{t(user_id, 'premium_status')} {t(user_id, 'active')}\n"
                    f"{t(user_id, 'plan')}: **{plan_name}**\n"
                    f"{t(user_id, 'expiry')}: **{formatted_expire}**\n"
                    f"{t(user_id, 'remaining')}: **{remaining}**"
                )

        else:

            profile_text = (
                f"{t(user_id, 'profile_title')}\n\n"
                f"{t(user_id, 'name')}: **{full_name}**\n"
                f"{t(user_id, 'username')}: **{username}**\n"
                f"{t(user_id, 'telegram_id')}: `{user_id}`\n\n"
                f"{t(user_id, 'premium_status')} {t(user_id, 'inactive')}\n"
                f"{t(user_id, 'plan')}: **{t(user_id, 'no_premium')}**\n\n"
                f"{t(user_id, 'premium_get')}"
            )


        profile_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    t(user_id, "get_premium"),
                    callback_data="premium"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "back"),
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

        await query.edit_message_text(
            t(user_id, "website_text"),
            reply_markup=back_keyboard
        )

        return


    # ----------------------------------
    # PREMIUM
    # ----------------------------------

    elif query.data == "premium":

        premium_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    t(user_id, "ref_method"),
                    callback_data="ref_method"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "buy"),
                    callback_data="buy_method"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "back"),
                    callback_data="back_to_start"
                )
            ]
        ])

        await query.edit_message_text(
            text=t(user_id, "premium_text"),
            reply_markup=premium_keyboard,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # REFERAL
    # ----------------------------------

    elif query.data == "ref_method":

        ref_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    t(user_id, "tutorial"),
                    url=TUTORIAL_GROUP_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "send_id"),
                    callback_data="send_id_prompt"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "back"),
                    callback_data="premium"
                )
            ]
        ])

        await query.edit_message_text(
            text=t(user_id, "ref_text"),
            reply_markup=ref_keyboard,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # BROKER ID
    # ----------------------------------

    elif query.data == "send_id_prompt":

        context.user_data["waiting_for_type"] = "broker_id"

        await query.edit_message_text(
            text=t(user_id, "send_id_text"),
            reply_markup=back_keyboard,
            parse_mode="Markdown"
        )

        return


    # ----------------------------------
    # SATYN ALMAK
    # ----------------------------------

    elif query.data == "buy_method":

        buy_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    t(user_id, "one_month"),
                    callback_data="plan_30"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "three_month"),
                    callback_data="plan_90"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "six_month"),
                    callback_data="plan_180"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "one_year"),
                    callback_data="plan_365"
                )
            ],
            [
                InlineKeyboardButton(
                    t(user_id, "back"),
                    callback_data="premium"
                )
            ]
        ])

        await query.edit_message_text(
            text=t(user_id, "buy_text"),
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
            "30": {
                "tk": "bir aýlyk",
                "tr": "1 aylık",
                "ru": "на 1 месяц",
                "en": "1 month"
            },
            "90": {
                "tk": "üç aýlyk",
                "tr": "3 aylık",
                "ru": "на 3 месяца",
                "en": "3 months"
            },
            "180": {
                "tk": "alty aýlyk",
                "tr": "6 aylık",
                "ru": "на 6 месяцев",
                "en": "6 months"
            },
            "365": {
                "tk": "bir ýyllyk",
                "tr": "1 yıllık",
                "ru": "на 1 год",
                "en": "1 year"
            }
        }.get(days, {}).get(
            get_user_language(user_id) or "tk",
            "bir aýlyk"
        )

        context.user_data["waiting_for_type"] = f"payment_{days}"

        await query.edit_message_text(
            text=t(
                user_id,
                "payment_text",
                month_label=month_label,
                price=price
            ),
            reply_markup=back_keyboard,
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
                text=t(
                    target_user_id,
                    "approved",
                    link=PREMIUM_GROUP_LINK
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
                text=t(
                    target_user_id,
                    "rejected"
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

        # ADMIN HABARY DIŇE TÜRKMENÇE

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
                t(user_id, "sent_admin")
            )

        except Exception:

            await update.message.reply_text(
                t(user_id, "admin_error")
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

            # ADMIN HABARY DIŇE TÜRKMENÇE

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
                t(user_id, "payment_sent")
            )

        except Exception:

            await update.message.reply_text(
                t(user_id, "payment_error")
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
                    text=t(
                        user_id,
                        "expired_message"
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
