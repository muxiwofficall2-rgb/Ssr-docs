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
SBOR = 500
DATA_FILE = "prices.json"
USERS_FILE = "users.json"

# ── FAYLLAR ──────────────────────────────────────────────────

def load_prices():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "Санкт-Петербург → Ташкент": 18500,
        "Санкт-Петербург → Самарканд": 19500,
        "Санкт-Петербург → Фергана": 20000,
        "Санкт-Петербург → Наманган": 19500,
        "Санкт-Петербург → Андижан": 20000,
        "Санкт-Петербург → Бухара": 21000,
        "Санкт-Петербург → Термез": 22000,
        "Санкт-Петербург → Карши": 22000,
        "Санкт-Петербург → Нукус": 23000,
        "Санкт-Петербург → Ургенч": 23000,
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
        users[uid] = {"username": username or "", "full_name": full_name or "", "count": 1}
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

# ── KLAVIATURALAR ─────────────────────────────────────────────

def main_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛂 Viza bo'limi", callback_data="visa_uz"),
             InlineKeyboardButton(text="✈️ Aviakassa", callback_data="aviation_uz")],
            [InlineKeyboardButton(text="📞 Tezkor aloqa", callback_data="contact_uz"),
             InlineKeyboardButton(text="📍 Manzil", callback_data="address_uz")],
            [InlineKeyboardButton(text="❓ Savol", callback_data="question_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛂 Визы", callback_data="visa_ru"),
             InlineKeyboardButton(text="✈️ Авиакасса", callback_data="aviation_ru")],
            [InlineKeyboardButton(text="📞 Быстрая связь", callback_data="contact_ru"),
             InlineKeyboardButton(text="📍 Адрес", callback_data="address_ru")],
            [InlineKeyboardButton(text="❓ Вопрос", callback_data="question_ru")],
            [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        ])

def back_kb(lang):
    text = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"home_{lang}")]
    ])

def visa_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Viza javobi", url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa")],
            [InlineKeyboardButton(text="🏛 O'zb Konsulstvo guruhi", url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="📝 Anketa to'ldirish", url="https://t.me/AVIAKASSA9094")],
            [InlineKeyboardButton(text="🇹🇲 Turkman fuqarolari uchun O'zb viza", callback_data="turkmen_uz")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Ответ по визе", url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa")],
            [InlineKeyboardButton(text="🏛 Группа Консульства Узб", url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="📝 Заполнить анкету", url="https://t.me/AVIAKASSA9094")],
            [InlineKeyboardButton(text="🇹🇲 Виза Узб для граждан Туркменистана", callback_data="turkmen_ru")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

def aviation_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094")],
            [InlineKeyboardButton(text="📱 IMO", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="🔵 Max", url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094")],
            [InlineKeyboardButton(text="📱 IMO", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="🔵 Max", url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

def contact_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 +7 981 193 90 94", url="tel:+79811939094")],
            [InlineKeyboardButton(text="📞 +7 921 402 74 89", url="tel:+79214027489")],
            [InlineKeyboardButton(text="📞 +7 937 949 90 94", url="tel:+79379499094")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 +7 981 193 90 94", url="tel:+79811939094")],
            [InlineKeyboardButton(text="📞 +7 921 402 74 89", url="tel:+79214027489")],
            [InlineKeyboardButton(text="📞 +7 937 949 90 94", url="tel:+79379499094")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

def address_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 1-manzil xaritada", url="https://yandex.ru/maps/-/CLaRUCPW")],
            [InlineKeyboardButton(text="🗺 2-manzil xaritada", url="https://yandex.ru/maps/org/omad_tour/50809406614")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Адрес 1 на карте", url="https://yandex.ru/maps/-/CLaRUCPW")],
            [InlineKeyboardButton(text="🗺 Адрес 2 на карте", url="https://yandex.ru/maps/org/omad_tour/50809406614")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

def prices_keyboard(lang):
    prices = load_prices()
    buttons = []
    for i, direction in enumerate(prices):
        buttons.append([InlineKeyboardButton(
            text=f"✈️ {direction}",
            callback_data=f"dir_{lang}_{i}"
        )])
    back_text = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data=f"aviation_{lang}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats")],
        [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="💰 Narxlar boshqaruvi", callback_data="adm_prices")],
    ])

def admin_prices_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Qo'shish", callback_data="adm_add"),
         InlineKeyboardButton(text="✏️ O'zgartirish", callback_data="adm_edit")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data="adm_delete"),
         InlineKeyboardButton(text="📋 Barchasi", callback_data="adm_list")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_back")],
    ])

# ── START ─────────────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(message: Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    text = "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\nXush kelibsiz! Bo'limni tanlang 👇"
    await message.answer(text, reply_markup=main_menu("uz"), parse_mode="HTML")

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🔧 <b>Admin panel</b>", reply_markup=admin_menu_kb(), parse_mode="HTML")

# ── TIL ───────────────────────────────────────────────────────

@dp.callback_query(F.data == "lang_uz")
async def lang_uz(callback: CallbackQuery):
    await callback.message.edit_text(
        "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\nXush kelibsiz! Bo'limni tanlang 👇",
        reply_markup=main_menu("uz"), parse_mode="HTML"
    )

@dp.callback_query(F.data == "lang_ru")
async def lang_ru(callback: CallbackQuery):
    await callback.message.edit_text(
        "✈️ <b>ОМАД ТУР</b> — Авиакасса\n\nДобро пожаловать! Выберите раздел 👇",
        reply_markup=main_menu("ru"), parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("home_"))
async def go_home(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    if lang == "uz":
        text = "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\nXush kelibsiz! Bo'limni tanlang 👇"
    else:
        text = "✈️ <b>ОМАД ТУР</b> — Авиакасса\n\nДобро пожаловать! Выберите раздел 👇"
    await callback.message.edit_text(text, reply_markup=main_menu(lang), parse_mode="HTML")

# ── VIZA ──────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("visa_"))
async def visa_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    if lang == "uz":
        text = "🛂 <b>Viza bo'limi</b>\n\nKerakli xizmatni tanlang 👇"
    else:
        text = "🛂 <b>Визовый раздел</b>\n\nВыберите нужную услугу 👇"
    await callback.message.edit_text(text, reply_markup=visa_menu(lang), parse_mode="HTML")

@dp.callback_query(F.data.startswith("turkmen_"))
async def turkmen_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    if lang == "uz":
        text = (
            "🇹🇲 <b>Turkmaniston fuqarolari uchun O'zbekiston vizasi</b>\n\n"
            "📋 <b>Kerakli hujjatlar:</b>\n"
            "• Pasport (6 oydan ko'p amal qilishi kerak)\n"
            "• 2 ta 3x4 rasm\n"
            "• To'ldirилган anketa\n"
            "• Taklif xati yoki mehmonxona bron\n"
            "• Viza to'lovi\n\n"
            "📞 Batafsil ma'lumot uchun bizga murojaat qiling:\n"
            "👇 Quyidagi tugmani bosing"
        )
    else:
        text = (
            "🇹🇲 <b>Виза Узбекистана для граждан Туркменистана</b>\n\n"
            "📋 <b>Необходимые документы:</b>\n"
            "• Паспорт (действителен более 6 месяцев)\n"
            "• 2 фото 3x4\n"
            "• Заполненная анкета\n"
            "• Приглашение или бронь отеля\n"
            "• Консульский сбор\n\n"
            "📞 Для подробной информации обратитесь к нам:\n"
            "👇 Нажмите кнопку ниже"
        )
    back_text = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Bog'lanish / Связаться", url="https://t.me/OMAD_TOUR9094")],
        [InlineKeyboardButton(text=back_text, callback_data=f"visa_{lang}")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── AVIAKASSA ─────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("aviation_"))
async def aviation_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    if lang == "uz":
        text = (
            "✈️ <b>Aviakassa — ОМАД ТУР</b>\n\n"
            "Санкт-Петербург dan O'zbekistonga\n"
            "arzon aviabiletlar!\n\n"
            "Biz bilan bog'laning 👇"
        )
    else:
        text = (
            "✈️ <b>Авиакасса — ОМАД ТУР</b>\n\n"
            "Авиабилеты из Санкт-Петербурга\n"
            "в Узбекистан по низким ценам!\n\n"
            "Свяжитесь с нами 👇"
        )
    await callback.message.edit_text(text, reply_markup=aviation_menu(lang), parse_mode="HTML")

# ── TEZKOR ALOQA ──────────────────────────────────────────────

@dp.callback_query(F.data.startswith("contact_"))
async def contact_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    if lang == "uz":
        text = (
            "📞 <b>Tezkor aloqa</b>\n\n"
            "Qo'ng'iroq qiling — doim yordam beramiz!\n\n"
            "📱 +7 981 193 90 94\n"
            "📱 +7 921 402 74 89\n"
            "📱 +7 937 949 90 94"
        )
    else:
        text = (
            "📞 <b>Быстрая связь</b>\n\n"
            "Звоните — всегда готовы помочь!\n\n"
            "📱 +7 981 193 90 94\n"
            "📱 +7 921 402 74 89\n"
            "📱 +7 937 949 90 94"
        )
    await callback.message.edit_text(text, reply_markup=contact_menu(lang), parse_mode="HTML")

# ── MANZIL ────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("address_"))
async def address_section(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    if lang == "uz":
        text = (
            "📍 <b>Bizning manzillar</b>\n\n"
            "🏢 ОМАД ТУР\n\n"
            "📌 1-офис: просп. Большевиков, 24, корп. 1\n"
            "📌 2-офис: ул. 4-я Красноармейская, дом 3\n\n"
            "🕐 Ish vaqti: 09:00 — 21:00 (har kuni)"
        )
    else:
        text = (
            "📍 <b>Наши адреса</b>\n\n"
            "🏢 ОМАД ТУР\n\n"
            "📌 Офис 1: просп. Большевиков, 24, корп. 1\n"
            "📌 Офис 2: ул. 4-я Красноармейская, дом 3\n\n"
            "🕐 Режим работы: 09:00 — 21:00 (ежедневно)"
        )
    await callback.message.edit_text(text, reply_markup=address_menu(lang), parse_mode="HTML")

# ── NARXLAR ───────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("prices_"))
async def show_prices(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    title = "✈️ <b>Yo'nalishni tanlang:</b>" if lang == "uz" else "✈️ <b>Выберите направление:</b>"
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
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📲 Buyurtma qilish", url="https://t.me/OMAD_TOUR9094")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="prices_uz")],
        ])
    else:
        text = (
            f"✈️ <b>{direction}</b>\n\n"
            f"💰 Цена: <b>{final_price:,} ₽</b>\n\n"
            f"📌 В цену включён багаж и сборы\n"
            f"📅 Цены могут меняться ежедневно\n\n"
            f"Для заказа билета 👇"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📲 Заказать билет", url="https://t.me/OMAD_TOUR9094")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="prices_ru")],
        ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── SAVOL ─────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("question_"))
async def question_section(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    if lang == "uz":
        text = "✉️ Savolingizni yozing\n(matn, rasm yoki fayl yuborishingiz mumkin):"
        back_text = "⬅️ Ortga"
    else:
        text = "✉️ Напишите ваш вопрос\n(можно отправить текст, фото или файл):"
        back_text = "⬅️ Назад"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_text, callback_data=f"home_{lang}")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await state.set_state(States.waiting_question)

@dp.message(States.waiting_question)
async def receive_question(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user = message.from_user
    username = f"@{user.username}" if user.username else "—"

    header = (
        f"📨 <b>Yangi savol</b>\n\n"
        f"👤 Ism: {user.full_name}\n"
        f"📱 Telegram: {username}\n"
        f"🆔 ID: <code>{user.id}</code>"
    )
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_{user.id}")]
    ])
    await bot.send_message(ADMIN_ID, header, reply_markup=reply_kb, parse_mode="HTML")

    # Xabarni adminga forward qilish (asl ko'rinishda)
    if message.text:
        await bot.send_message(ADMIN_ID, f"💬 <b>Savol:</b>\n{message.text}", parse_mode="HTML")
    elif message.photo:
        caption = f"🖼 <b>Rasm bilan savol:</b>\n{message.caption or ''}"
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, parse_mode="HTML")
    elif message.document:
        caption = f"📄 <b>Fayl bilan savol:</b>\n{message.caption or ''}"
        await bot.send_document(ADMIN_ID, message.document.file_id, caption=caption, parse_mode="HTML")
    elif message.video:
        caption = f"🎥 <b>Video bilan savol:</b>\n{message.caption or ''}"
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=caption, parse_mode="HTML")
    elif message.voice:
        await bot.send_voice(ADMIN_ID, message.voice.file_id)
        await bot.send_message(ADMIN_ID, "🎤 <b>Ovozli xabar</b>", parse_mode="HTML")
    elif message.sticker:
        await bot.send_sticker(ADMIN_ID, message.sticker.file_id)

    # Foydalanuvchiga tasdiqlash
    if lang == "uz":
        confirm = "✅ Murojaatingiz qabul qilindi!\nIltimos javobni kuting. 🙏"
    else:
        confirm = "✅ Ваш запрос принят!\nПожалуйста, ожидайте ответа. 🙏"
    await message.answer(confirm, reply_markup=main_menu(lang))
    await state.clear()

# ── ADMIN JAVOB ───────────────────────────────────────────────

@dp.callback_query(F.data.startswith("reply_"))
async def reply_to_user(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split("_")[1])
    await state.update_data(reply_to=user_id)
    await callback.message.answer("✏️ Javobingizni yozing (matn, rasm, video):")
    await state.set_state(States.waiting_reply)

@dp.message(States.waiting_reply)
async def send_reply(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    user_id = data.get("reply_to")
    try:
        if message.text:
            await bot.send_message(user_id, f"📬 <b>ОМАД ТУР dan javob:</b>\n\n{message.text}", parse_mode="HTML")
        elif message.photo:
            caption = f"📬 <b>ОМАД ТУР dan javob:</b>\n{message.caption or ''}"
            await bot.send_photo(user_id, message.photo[-1].file_id, caption=caption, parse_mode="HTML")
        elif message.video:
            caption = f"📬 <b>ОМАД ТУР dan javob:</b>\n{message.caption or ''}"
            await bot.send_video(user_id, message.video.file_id, caption=caption, parse_mode="HTML")
        elif message.document:
            caption = f"📬 <b>ОМАД ТУР dan javob:</b>\n{message.caption or ''}"
            await bot.send_document(user_id, message.document.file_id, caption=caption, parse_mode="HTML")
        await message.answer("✅ Javob foydalanuvchiga yuborildi!")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    await state.clear()

# ── ADMIN PANEL ───────────────────────────────────────────────

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
        f"<b>So'nggi foydalanuvchilar:</b>\n\n"
    )
    for i, (uid, u) in enumerate(list(users.items())[-15:]):
        uname = f"@{u['username']}" if u.get("username") else "—"
        text += f"{i+1}. {u['full_name']} {uname}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_back")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer(
        "📢 Foydalanuvchilarga yuboriladigan xabarni yozing\n"
        "(matn, rasm, video yoki fayl):"
    )
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
    await message.answer(
        f"✅ Yuborildi: <b>{success}</b> ta\n❌ Xato: <b>{fail}</b> ta",
        reply_markup=admin_menu_kb(), parse_mode="HTML"
    )
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
    await callback.message.answer(
        "➕ Yangi yo'nalish nomini yozing:\n<i>Masalan: Санкт-Петербург → Навои</i>",
        parse_mode="HTML"
    )
    await state.set_state(States.admin_add_direction)

@dp.message(States.admin_add_direction)
async def adm_get_direction(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(direction=message.text)
    await message.answer(
        f"✅ Yo'nalish: <b>{message.text}</b>\n\nNarxni kiriting (sborsiz):",
        parse_mode="HTML"
    )
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
    text = "✏️ Qaysi yo'nalishni o'zgartirish?\nRaqamini yozing:\n\n"
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
        await message.answer(
            f"✏️ <b>{directions[idx]}</b>\n\nYangi narxni kiriting:",
            parse_mode="HTML"
        )
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
            f"✅ Yangilandi!\n📍 {direction}\n💰 {price:,} ₽ → {price+SBOR:,} ₽",
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
    text = "🗑 Qaysi yo'nalishni o'chirish?\nRaqamini yozing:\n\n"
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
        await message.answer(
            f"✅ O'chirildi: {direction}",
            reply_markup=admin_prices_kb()
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

# ── MAIN ──────────────────────────────────────────────────────

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
