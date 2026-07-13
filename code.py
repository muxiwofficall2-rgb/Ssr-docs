import os
import logging
import sqlite3
from datetime import time

import requests
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------- CONFIG (Railway -> Variables bo'limidan olinadi) ----------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@AVIAKASSA9094")
DB_PATH = os.environ.get("DB_PATH", "bot.db")

ADDRESS_TEXT = (
    "📍 Manzil: 4-я Красноармейская, дом 3 (домофон 22В)\n"
    "🚇 Metro: Технологический институт\n\n"
    "☎️ Aloqa uchun pastdagi \"Admin bilan bog'lanish\" tugmasini bosing."
)
PRICES_TEXT = (
    "💰 Xizmatlarimiz:\n"
    "— ✈️ Aviachipta (Rossiya ⇄ O'zbekiston)\n"
    "— 📝 Notarial va tarjima xizmatlari\n"
    "— 🖨 Nusxa ko'chirish / bosib chiqarish\n\n"
    "Aniq narx uchun \"Buyurtma berish\" orqali murojaat qiling — operator tez orada bog'lanadi."
)

# ---------------- DATABASE ----------------

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS orders(
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            phone TEXT,
            service TEXT,
            status TEXT DEFAULT 'yangi',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    return conn


def save_user(user):
    conn = db()
    conn.execute(
        "INSERT OR IGNORE INTO users(user_id, username, first_name) VALUES (?,?,?)",
        (user.id, user.username, user.first_name),
    )
    conn.commit()
    conn.close()


def save_order(user_id, full_name, phone, service):
    conn = db()
    cur = conn.execute(
        "INSERT INTO orders(user_id, full_name, phone, service) VALUES (?,?,?,?)",
        (user_id, full_name, phone, service),
    )
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    return order_id


def update_order_status(order_id, status):
    conn = db()
    conn.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
    conn.commit()
    conn.close()


def get_stats():
    conn = db()
    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    today_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE date(created_at)=date('now')"
    ).fetchone()[0]
    conn.close()
    return users_count, orders_count, today_orders


def get_all_user_ids():
    conn = db()
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [r[0] for r in rows]


# ---------------- KEYBOARDS ----------------

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🛫 Buyurtma berish"],
        ["📍 Manzil / Aloqa", "💰 Narxlar / Xizmatlar"],
        ["💱 Valyuta kursi", "🌤 Ob-havo"],
        ["👤 Admin bilan bog'lanish"],
    ],
    resize_keyboard=True,
)

# ---------------- CONVERSATION STATES ----------------
NAME, PHONE, SERVICE = range(3)

# ---------------- BASIC HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user)
    await update.message.reply_text(
        "Assalomu alaykum! OMAD botiga xush kelibsiz ✈️📝🖨\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=MAIN_MENU,
    )


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ADDRESS_TEXT)


async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(PRICES_TEXT)


async def admin_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Admin bilan bog'lanish uchun: tg://user?id=" + str(ADMIN_ID)
    )


# ---------------- ORDER FLOW ----------------

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ismingizni kiriting (bekor qilish uchun /cancel):"
    )
    return NAME


async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text(
        "Telefon raqamingizni kiriting (+998... yoki +7...):"
    )
    return PHONE


async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text(
        "Qaysi xizmat kerak? (masalan: aviachipta, notarius, nusxa ko'chirish)"
    )
    return SERVICE


async def order_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = context.user_data["full_name"]
    phone = context.user_data["phone"]
    service = update.message.text
    order_id = save_order(user.id, full_name, phone, service)

    text = (
        f"🆕 Yangi buyurtma #{order_id}\n"
        f"👤 {full_name}\n"
        f"📞 {phone}\n"
        f"🧾 {service}\n"
        f"🔗 tg://user?id={user.id}"
    )
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Qabul qilindi", callback_data=f"ok_{order_id}"),
                InlineKeyboardButton("❌ Bekor qilindi", callback_data=f"no_{order_id}"),
            ]
        ]
    )
    await context.bot.send_message(ADMIN_ID, text, reply_markup=kb)
    try:
        await context.bot.send_message(CHANNEL_ID, text)
    except Exception as e:
        logger.warning(f"Kanalga yuborilmadi: {e}")

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        reply_markup=MAIN_MENU,
    )
    context.user_data.clear()
    return ConversationHandler.END


async def order_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Bekor qilindi.", reply_markup=MAIN_MENU)
    return ConversationHandler.END


async def order_status_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, order_id = query.data.split("_")
    status = "✅ tasdiqlandi" if action == "ok" else "❌ bekor qilindi"
    update_order_status(order_id, status)
    await query.edit_message_text(query.message.text + f"\n\nHolat: {status}")


# ---------------- CURRENCY & WEATHER ----------------

def fetch_currency():
    try:
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/", timeout=10)
        data = r.json()
        rates = {item["Ccy"]: item["Rate"] for item in data}
        return rates.get("USD"), rates.get("RUB")
    except Exception as e:
        logger.error(f"Kurs xatosi: {e}")
        return None, None


def fetch_weather():
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 59.9343,
                "longitude": 30.3351,
                "current_weather": True,
            },
            timeout=10,
        )
        data = r.json()["current_weather"]
        return data["temperature"], data["windspeed"]
    except Exception as e:
        logger.error(f"Ob-havo xatosi: {e}")
        return None, None


async def currency_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usd, rub = fetch_currency()
    if usd:
        await update.message.reply_text(
            f"💱 Bugungi rasmiy kurs (CBU, so'mda):\n"
            f"1 USD = {usd} so'm\n"
            f"1 RUB = {rub} so'm"
        )
    else:
        await update.message.reply_text(
            "Kursni olishda xatolik yuz berdi, birozdan keyin urinib ko'ring."
        )


async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    temp, wind = fetch_weather()
    if temp is not None:
        await update.message.reply_text(
            f"🌤 Sankt-Peterburgda hozir: {temp}°C, shamol {wind} km/soat"
        )
    else:
        await update.message.reply_text(
            "Ob-havoni olishda xatolik yuz berdi, birozdan keyin urinib ko'ring."
        )


async def daily_job(context: ContextTypes.DEFAULT_TYPE):
    usd, rub = fetch_currency()
    temp, wind = fetch_weather()
    text = "📅 Kunlik yangilanish\n\n"
    if usd:
        text += f"💱 1 USD = {usd} so'm | 1 RUB = {rub} so'm\n"
    if temp is not None:
        text += f"🌤 Sankt-Peterburg: {temp}°C\n"
    try:
        await context.bot.send_message(CHANNEL_ID, text)
    except Exception as e:
        logger.warning(f"Kunlik xabar yuborilmadi: {e}")


# ---------------- ADMIN PANEL ----------------

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📊 Statistika", callback_data="stat")],
            [InlineKeyboardButton("📢 Reklama yuborish", callback_data="bc_start")],
        ]
    )
    await update.message.reply_text("🛠 Admin panel:", reply_markup=kb)


async def admin_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer()
        return
    await query.answer()
    if query.data == "stat":
        users, orders, today = get_stats()
        await query.message.reply_text(
            f"📊 Statistika:\n"
            f"👥 Foydalanuvchilar: {users}\n"
            f"🧾 Jami buyurtmalar: {orders}\n"
            f"📆 Bugungi buyurtmalar: {today}"
        )
    elif query.data == "bc_start":
        context.user_data["awaiting_broadcast"] = True
        await query.message.reply_text(
            "📢 Reklama uchun matn / rasm / video / fayl yuboring:"
        )


async def admin_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Faqat admindan keladigan xabarlarni reklama oqimi uchun tutib qoladi."""
    if update.effective_user.id != ADMIN_ID:
        return

    if context.user_data.get("awaiting_broadcast"):
        context.user_data["broadcast_message"] = update.message
        context.user_data["awaiting_broadcast"] = False
        context.user_data["awaiting_button"] = True
        await update.message.reply_text(
            "Xabarga inline tugma qo'shasizmi?\n"
            "Format: Tugma matni - https://link\n"
            "Kerak bo'lmasa \"yo'q\" deb yozing."
        )
        return

    if context.user_data.get("awaiting_button"):
        context.user_data["awaiting_button"] = False
        text = (update.message.text or "").strip()
        markup = None
        if text.lower() != "yo'q" and "-" in text:
            label, url = text.split("-", 1)
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(label.strip(), url=url.strip())]]
            )
        context.user_data["broadcast_markup"] = markup
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✅ Yuborish", callback_data="bc_send")],
                [InlineKeyboardButton("❌ Bekor qilish", callback_data="bc_cancel")],
            ]
        )
        await update.message.reply_text("Shu xabarni barchaga yuborishni tasdiqlaysizmi?", reply_markup=kb)


async def broadcast_confirm_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer()
        return
    await query.answer()

    if query.data == "bc_send":
        msg = context.user_data.get("broadcast_message")
        markup = context.user_data.get("broadcast_markup")
        if not msg:
            await query.message.reply_text("Xabar topilmadi, qaytadan boshlang.")
            return
        sent, failed = 0, 0
        for uid in get_all_user_ids():
            try:
                await msg.copy(chat_id=uid, reply_markup=markup)
                sent += 1
            except Exception:
                failed += 1
        await query.message.reply_text(f"✅ Yuborildi: {sent} ta\n❌ Yetib bormadi: {failed} ta")
        context.user_data.pop("broadcast_message", None)
        context.user_data.pop("broadcast_markup", None)
    elif query.data == "bc_cancel":
        context.user_data.pop("broadcast_message", None)
        context.user_data.pop("broadcast_markup", None)
        await query.message.reply_text("Bekor qilindi.")


# ---------------- MAIN ----------------

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    order_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🛫 Buyurtma berish$"), order_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_service)],
        },
        fallbacks=[CommandHandler("cancel", order_cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(order_conv)
    app.add_handler(MessageHandler(filters.Regex("^📍 Manzil / Aloqa$"), address))
    app.add_handler(MessageHandler(filters.Regex("^💰 Narxlar / Xizmatlar$"), prices))
    app.add_handler(MessageHandler(filters.Regex("^👤 Admin bilan bog'lanish$"), admin_contact))
    app.add_handler(MessageHandler(filters.Regex("^💱 Valyuta kursi$"), currency_cmd))
    app.add_handler(MessageHandler(filters.Regex("^🌤 Ob-havo$"), weather_cmd))

    app.add_handler(CallbackQueryHandler(order_status_cb, pattern="^(ok|no)_"))
    app.add_handler(CallbackQueryHandler(admin_cb, pattern="^(stat|bc_start)$"))
    app.add_handler(CallbackQueryHandler(broadcast_confirm_cb, pattern="^bc_(send|cancel)$"))

    # Reklama oqimi uchun admin xabarlarini eng oxirida tutamiz
    app.add_handler(MessageHandler(filters.ALL & filters.User(ADMIN_ID), admin_flow))

    app.job_queue.run_daily(daily_job, time=time(hour=8, minute=0))

    logger.info("Bot ishga tushdi (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
