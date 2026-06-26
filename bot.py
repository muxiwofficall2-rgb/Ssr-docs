import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8949050831:AAHqp6G4hmoiAfYvf095_KN3GjTvIdFtWwY"
ADMIN_ID = 7359558983
SBOR = 1000

DATA_FILE = "prices.json"
USERS_FILE = "users.json"

# ── FAYLLAR ──────────────────────────────────────────────────

def load_prices():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "Санкт-Петербург → Ташкент": 16223,
        "Санкт-Петербург → Самарканд": 18224,
        "Санкт-Петербург → Фергана": 13120,
        "Санкт-Петербург → Наманган": 19500,
        "Санкт-Петербург → Андижан": 22596,
        "Санкт-Петербург → Бухара": 18998,
        "Санкт-Петербург → Термез": 20149,
        "Санкт-Петербург → Карши": 18652,
        "Санкт-Петербург → Нукус": 16443,
        "Санкт-Петербург → Ургенч": 12936,
    }

def save_prices(prices):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user(user_id, username, full_name):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"username": username, "full_name": full_name, "count": 1}
    else:
        users[uid]["count"] += 1
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ── BOT ──────────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class States(StatesGroup):
    waiting_question = State()
    waiting_broadcast = State()
    waiting_reply = State()
    admin_add_direction = State()
    admin_add_price = State()
    admin_edit_select = State()
    admin_edit_price = State()
    admin_delete_select = State()

# ── TILLAR ───────────────────────────────────────────────────

T = {
    "uz": {
        "start": "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\nXush kelibsiz! Bo'limni tanlang 👇",
        "visa": "🛂 Viza bo'limi",
        "aviation": "✈️ Aviakassa",
        "contact": "📞 Tezkor aloqa",
        "address": "📍 Manzil",
        "question": "❓ Savol",
        "back": "⬅️ Ortga",
        "lang": "🌍 Til",
        "prices": "💰 Narxlar",
        "order": "📲 Buyurtma qilish",
        "visa_answer": "📋 Viza javobi",
        "uzb_consul": "🏛 O'zb Konsulstvo guruhi",
        "anketa": "📝 Anketa to'ldirish",
        "question_send": "✉️ Savolingizni yozing (matn, rasm yoki fayl):",
        "question_sent": "✅ Murojaatingiz qabul qilindi!\nIltimos javobni kuting.",
        "question_new": "📨 Yangi savol",
        "reply_btn": "💬 Javob berish",
        "admin": "🔧 Admin panel",
        "admin_stats": "📊 Statistika",
        "admin_broadcast": "📢 Xabar yuborish",
        "admin_prices": "💰 Narxlar boshqaruvi",
        "add_direction": "➕ Yo'nalish qo'shish",
        "edit_direction": "✏️ Narx o'zgartirish",
        "delete_direction": "🗑 Yo'nalish o'chirish",
        "all_prices": "📋 Barcha narxlar",
        "broadcast_ask": "📢 Foydalanuvchilarga yuboriladigan xabarni yozing (matn, rasm, video):",
        "broadcast_done": "✅ Xabar barcha foydalanuvchilarga yuborildi!",
        "call": "📞 Qo'ng'iroq qilish",
    },
    "ru": {
        "start": "✈️ <b>ОМАД ТУР</b> — Авиакасса\n\nДобро пожаловать! Выберите раздел 👇",
        "visa": "🛂 Визы",
        "aviation": "✈️ Авиакасса",
        "contact": "📞 Быстрая связь",
        "address": "📍 Адрес",
        "question": "❓ Вопрос",
        "back": "⬅️ Назад",
        "lang": "🌍 Язык",
        "prices": "💰 Цены",
        "order": "📲 Заказать билет",
        "visa_answer": "📋 Ответ по визе",
        "uzb_consul": "🏛 Группа Консульства Узб",
        "anketa": "📝 Заполнить анкету",
        "question_send": "✉️ Напишите ваш вопрос (текст, фото или файл):",
        "question_sent": "✅ Ваш запрос принят!\nПожалуйста, ожидайте ответа.",
        "question_new": "📨 Новый вопрос",
        "reply_btn": "💬 Ответить",
        "admin": "🔧 Админ панель",
        "admin_stats": "📊 Статистика",
        "admin_broadcast": "📢 Рассылка",
        "admin_prices": "💰 Управление ценами",
        "add_direction": "➕ Добавить направление",
        "edit_direction": "✏️ Изменить цену",
        "delete_direction": "🗑 Удалить направление",
        "all_prices": "📋 Все цены",
        "broadcast_ask": "📢 Напишите сообщение для рассылки (текст, фото, видео):",
        "broadcast_done": "✅ Сообщение отправлено всем пользователям!",
        "call": "📞 Позвонить",
    }
}

def t(lang, key):
    return T.get(lang, T["uz"]).get(key, key)

# ── KLAVIATURALAR ────────────────────────────────────────────

def main_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"visa"), callback_data=f"visa_{lang}"),
         InlineKeyboardButton(text=t(lang,"aviation"), callback_data=f"aviation_{lang}")],
        [InlineKeyboardButton(text=t(lang,"contact"), callback_data=f"contact_{lang}"),
         InlineKeyboardButton(text=t(lang,"address"), callback_data=f"address_{lang}")],
        [InlineKeyboardButton(text=t(lang,"question"), callback_data=f"question_{lang}")],
        [InlineKeyboardButton(text="🇺🇿 O'zbek" if lang=="ru" else "🇷🇺 Русский",
                              callback_data="lang_ru" if lang=="uz" else "lang_uz")],
    ])

def back_btn(lang, to="home"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"back"), callback_data=f"home_{lang}")]
    ])

def visa_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"visa_answer"),
                              url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa")],
        [InlineKeyboardButton(text=t(lang,"uzb_consul"),
                              url="https://t.me/+i8I6ByH_CUVhOWQy")],
        [InlineKeyboardButton(text=t(lang,"anketa"),
                              url="https://t.me/AVIAKASSA9094")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data=f"home_{lang}")],
    ])

def aviation_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094")],
        [InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094")],
        [InlineKeyboardButton(text="📱 IMO", url="https://t.me/OMAD_TOUR9094")],
        [InlineKeyboardButton(text="🔵 Max", url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk")],
        [InlineKeyboardButton(text=t(lang,"prices"), callback_data=f"prices_{lang}")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data=f"home_{lang}")],
    ])

def contact_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 +7 981 193 90 94", url="tel:+79811939094")],
        [InlineKeyboardButton(text="📞 +7 921 402 74 89", url="tel:+79214027489")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data=f"home_{lang}")],
    ])

def address_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Yandex Xarita", url="https://yandex.ru/maps/org/omad_tour/50809406614")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data=f"home_{lang}")],
    ])

def prices_keyboard(lang):
    prices = load_prices()
    buttons = []
    for i, direction in enumerate(prices):
        buttons.append([InlineKeyboardButton(
            text=f"✈️ {direction}",
            callback_data=f"dir_{lang}_{i}"
        )])
    buttons.append([InlineKeyboardButton(text=t(lang,"back"), callback_data=f"aviation_{lang}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats")],
        [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="💰 Narxlar", callback_data="adm_prices")],
    ])

def admin_prices_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Qo'shish", callback_data="adm_add")],
        [InlineKeyboardButton(text="✏️ O'zgartirish", callback_data="adm_edit")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data="adm_delete")],
        [InlineKeyboardButton(text="📋 Barchasi", callback_data="adm_list")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_back")],
    ])

# ── START ────────────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(message: Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(t("uz","start"), reply_markup=main_menu("uz"), parse_mode="HTML")

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🔧 <b>Admin panel</b>", reply_markup=admin_menu_kb(), parse_mode="HTML")

# ── TIL ──────────────────────────────────────────────────────

@dp.callback_query(F.data == "lang_uz")
async def lang_uz(callback: CallbackQuery):
    await callback.message.edit_text(t("uz","start"), reply_markup=main_menu("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "lang_ru")
async def lang_ru(callback: CallbackQuery):
    await callback.message.edit_text(t("ru","start"), reply_markup=main_menu("ru"), parse_mode="HTML")

# ── HOME ─────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("home_"))
async def go_home(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await callback.message.edit_text(t(lang,"start"), reply_markup=main_menu(lang), parse_mode="HTML")

# ── VIZA ─────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("visa_"))
async def visa_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    text_uz = (
        "🛂 <b>Viza bo'limi</b>\n\n"
        "O'zbekiston fuqarolari uchun viza xizmatlari:\n\n"
        "📋 Viza javobi — barcode orqali tekshirish\n"
        "🏛 Konsulstvo guruhi — rasmiy ma'lumotlar\n"
        "📝 Anketa to'ldirish — onlayn ariza"
    )
    text_ru = (
        "🛂 <b>Визовый раздел</b>\n\n"
        "Визовые услуги для граждан Узбекистана:\n\n"
        "📋 Ответ по визе — проверка по штрихкоду\n"
        "🏛 Группа консульства — официальная информация\n"
        "📝 Заполнить анкету — онлайн заявка"
    )
    text = text_uz if lang == "uz" else text_ru
    await callback.message.edit_text(text, reply_markup=visa_menu(lang), parse_mode="HTML")

# ── AVIAKASSA ────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("aviation_"))
async def aviation_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    text_uz = (
        "✈️ <b>Aviakassa — ОМАД ТУР</b>\n\n"
        "Санкт-Петербург dan O'zbekistonga\n"
        "arzon aviabiletlar!\n\n"
        "Biz bilan bog'laning:"
    )
    text_ru = (
        "✈️ <b>Авиакасса — ОМАД ТУР</b>\n\n"
        "Авиабилеты из Санкт-Петербурга\n"
        "в Узбекистан по низким ценам!\n\n"
        "Свяжитесь с нами:"
    )
    text = text_uz if lang == "uz" else text_ru
    await callback.message.edit_text(text, reply_markup=aviation_menu(lang), parse_mode="HTML")

# ── NARXLAR ──────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("prices_"))
async def show_prices(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    title = "✈️ <b>Yo'nalishni tanlang:</b>" if lang=="uz" else "✈️ <b>Выберите направление:</b>"
    await callback.message.edit_text(title, reply_markup=prices_keyboard(lang), parse_mode="HTML")

@dp.callback_query(F.data.startswith("dir_"))
async def show_direction(callback: CallbackQuery):
    parts = callback.data.split("_")
    lang = parts[1]
    idx = int(parts[2])
    prices = load_prices()
    directions = list(prices.keys())
    if idx >= len(directions):
        await callback.answer("Topilmadi!")
        return
    direction = directions[idx]
    final_price = prices[direction] + SBOR
    if lang == "uz":
        text = (
            f"✈️ <b>{direction}</b>\n\n"
            f"💰 Narx: <b>{final_price:,} ₽</b>\n\n"
            f"📌 Narxga bagaj va xizmat to'lovlari kiradi\n"
            f"📅 Narxlar har kuni o'zgarishi mumkin\n\n"
            f"Bilet buyurtma qilish uchun 👇"
        )
    else:
        text = (
            f"✈️ <b>{direction}</b>\n\n"
            f"💰 Цена: <b>{final_price:,} ₽</b>\n\n"
            f"📌 В цену включён багаж и сборы\n"
            f"📅 Цены могут меняться ежедневно\n\n"
            f"Для заказа билета 👇"
        )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"order"), url="https://t.me/OMAD_TOUR9094")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data=f"prices_{lang}")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── TEZKOR ALOQA ─────────────────────────────────────────────

@dp.callback_query(F.data.startswith("contact_"))
async def contact_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    text_uz = (
        "📞 <b>Tezkor aloqa</b>\n\n"
        "Qo'ng'iroq qiling — doim yordam beramiz!\n\n"
        "📱 +7 981 193 90 94\n"
        "📱 +7 921 402 74 89"
    )
    text_ru = (
        "📞 <b>Быстрая связь</b>\n\n"
        "Звоните — всегда готовы помочь!\n\n"
        "📱 +7 981 193 90 94\n"
        "📱 +7 921 402 74 89"
    )
    text = text_uz if lang == "uz" else text_ru
    await callback.message.edit_text(text, reply_markup=contact_menu(lang), parse_mode="HTML")

# ── MANZIL ───────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("address_"))
async def address_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    text_uz = (
        "📍 <b>Bizning manzil</b>\n\n"
        "🏢 ОМАД ТУР\n"
        "просп. Большевиков, 24, корп. 1\n"
        "Санкт-Петербург\n\n"
        "🕐 Ish vaqti: 09:00 — 21:00 (har kuni)"
    )
    text_ru = (
        "📍 <b>Наш адрес</b>\n\n"
        "🏢 ОМАД ТУР\n"
        "просп. Большевиков, 24, корп. 1\n"
        "Санкт-Петербург\n\n"
        "🕐 Режим работы: 09:00 — 21:00 (ежедневно)"
    )
    text = text_uz if lang == "uz" else text_ru
    await callback.message.edit_text(text, reply_markup=address_menu(lang), parse_mode="HTML")

# ── SAVOL ────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("question_"))
async def question_section(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"back"), callback_data=f"home_{lang}")]
    ])
    await callback.message.edit_text(t(lang,"question_send"), reply_markup=kb, parse_mode="HTML")
    await state.set_state(States.waiting_question)

@dp.message(States.waiting_question)
async def receive_question(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user = message.from_user
    username = f"@{user.username}" if user.username else "yo'q"

    # Admin ga xabar
    admin_text = (
        f"📨 <b>Yangi savol</b>\n\n"
        f"👤 Ism: {user.full_name}\n"
        f"📱 Telegram: {username}\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"💬 Savol:"
    )
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_{user.id}")]
    ])

    await bot.send_message(ADMIN_ID, admin_text, reply_markup=reply_kb, parse_mode="HTML")

    # Savolni adminga forward qilish
    if message.text:
        await bot.send_message(ADMIN_ID, f"📝 {message.text}")
    elif message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=message.caption or "")
    elif message.document:
        await bot.send_document(ADMIN_ID, message.document.file_id, caption=message.caption or "")
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=message.caption or "")

    # Foydalanuvchiga tasdiqlash
    await message.answer(t(lang, "question_sent"), reply_markup=main_menu(lang), parse_mode="HTML")
    await state.clear()

# ── ADMIN JAVOB BERISH ───────────────────────────────────────

@dp.callback_query(F.data.startswith("reply_"))
async def reply_to_user(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split("_")[1])
    await state.update_data(reply_to=user_id)
    await callback.message.answer("✏️ Javobingizni yozing:")
    await state.set_state(States.waiting_reply)

@dp.message(States.waiting_reply)
async def send_reply(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    user_id = data.get("reply_to")
    try:
        reply_text = f"📬 <b>ОМАД ТУР javob berdi:</b>\n\n{message.text}"
        await bot.send_message(user_id, reply_text, parse_mode="HTML")
        await message.answer("✅ Javob yuborildi!")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    await state.clear()

# ── ADMIN PANEL ──────────────────────────────────────────────

@dp.callback_query(F.data == "adm_back")
async def adm_back(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("🔧 <b>Admin panel</b>", reply_markup=admin_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_stats")
async def adm_stats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    users = load_users()
    total = len(users)
    total_visits = sum(u["count"] for u in users.values())
    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"🔢 Jami tashriflar: <b>{total_visits}</b>\n\n"
        f"<b>So'nggi 10 foydalanuvchi:</b>\n"
    )
    for i, (uid, u) in enumerate(list(users.items())[-10:]):
        uname = f"@{u['username']}" if u.get('username') else "—"
        text += f"{i+1}. {u['full_name']} {uname} ({u['count']} marta)\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_back")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("📢 Foydalanuvchilarga yuboriladigan xabarni yozing\n(matn, rasm yoki video):")
    await state.set_state(States.waiting_broadcast)

@dp.message(States.waiting_broadcast)
async def send_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    success = 0
    fail = 0
    for uid in users:
        try:
            if message.text:
                await bot.send_message(int(uid), message.text)
            elif message.photo:
                await bot.send_photo(int(uid), message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await bot.send_video(int(uid), message.video.file_id, caption=message.caption or "")
            elif message.document:
                await bot.send_document(int(uid), message.document.file_id, caption=message.caption or "")
            success += 1
        except:
            fail += 1
    await message.answer(f"✅ Yuborildi: {success}\n❌ Xato: {fail}", reply_markup=admin_menu_kb())
    await state.clear()

@dp.callback_query(F.data == "adm_prices")
async def adm_prices(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("💰 <b>Narxlar boshqaruvi</b>", reply_markup=admin_prices_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_list")
async def adm_list(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    text = "📋 <b>Joriy narxlar:</b>\n\n"
    for i, (d, p) in enumerate(prices.items()):
        text += f"{i+1}. {d}\n   💰 {p:,} ₽ → mijoz: {p+SBOR:,} ₽\n\n"
    await callback.message.edit_text(text, reply_markup=admin_prices_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_add")
async def adm_add(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("➕ Yangi yo'nalish nomini yozing:\n<i>Масalan: Санкт-Петербург → Навои</i>", parse_mode="HTML")
    await state.set_state(States.admin_add_direction)

@dp.message(States.admin_add_direction)
async def adm_get_direction(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(direction=message.text)
    await message.answer(f"✅ Yo'nalish: <b>{message.text}</b>\n\nNarxni kiriting (sborsiz):", parse_mode="HTML")
    await state.set_state(States.admin_add_price)

@dp.message(States.admin_add_price)
async def adm_get_price(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
        data = await state.get_data()
        direction = data["direction"]
        prices = load_prices()
        prices[direction] = price
        save_prices(prices)
        await message.answer(
            f"✅ <b>Saqlandi!</b>\n\n📍 {direction}\n💰 Asl: {price:,} ₽\n👤 Mijoz: {price+SBOR:,} ₽",
            reply_markup=admin_prices_kb(), parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

@dp.callback_query(F.data == "adm_edit")
async def adm_edit(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    text = "✏️ Qaysi yo'nalishni o'zgartirish? Raqamini yozing:\n\n"
    for i, (d, p) in enumerate(prices.items()):
        text += f"{i+1}. {d} — {p:,} ₽\n"
    await callback.message.answer(text)
    await state.set_state(States.admin_edit_select)

@dp.message(States.admin_edit_select)
async def adm_edit_select(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        idx = int(message.text.strip()) - 1
        prices = load_prices()
        directions = list(prices.keys())
        if idx < 0 or idx >= len(directions):
            await message.answer("❌ Noto'g'ri raqam!")
            return
        await state.update_data(direction=directions[idx])
        await message.answer(f"✏️ <b>{directions[idx]}</b>\n\nYangi narxni kiriting:", parse_mode="HTML")
        await state.set_state(States.admin_edit_price)
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

@dp.message(States.admin_edit_price)
async def adm_edit_price(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
        data = await state.get_data()
        direction = data["direction"]
        prices = load_prices()
        prices[direction] = price
        save_prices(prices)
        await message.answer(
            f"✅ Yangilandi!\n{direction}\n💰 {price:,} ₽ → {price+SBOR:,} ₽",
            reply_markup=admin_prices_kb(), parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

@dp.callback_query(F.data == "adm_delete")
async def adm_delete(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    text = "🗑 Qaysi yo'nalishni o'chirish? Raqamini yozing:\n\n"
    for i, (d, p) in enumerate(prices.items()):
        text += f"{i+1}. {d} — {p:,} ₽\n"
    await callback.message.answer(text)
    await state.set_state(States.admin_delete_select)

@dp.message(States.admin_delete_select)
async def adm_delete_select(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        idx = int(message.text.strip()) - 1
        prices = load_prices()
        directions = list(prices.keys())
        if idx < 0 or idx >= len(directions):
            await message.answer("❌ Noto'g'ri raqam!")
            return
        direction = directions[idx]
        del prices[direction]
        save_prices(prices)
        await message.answer(f"✅ O'chirildi: {direction}", reply_markup=admin_prices_kb())
        await state.clear()
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

# ── ISHGA TUSHIRISH ──────────────────────────────────────────

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
