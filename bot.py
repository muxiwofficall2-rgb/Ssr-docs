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

# ── BOSH MENU ─────────────────────────────────────────────────

def main_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛂 Viza bo'limi", callback_data="visa_uz"),
             InlineKeyboardButton(text="✈️ Aviakassa", callback_data="aviation_uz")],
            [InlineKeyboardButton(text="📞 Tezkor aloqa", callback_data="contact_uz"),
             InlineKeyboardButton(text="📍 Manzil", callback_data="address_uz")],
            [InlineKeyboardButton(text="❓ Savol yuborish", callback_data="question_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="lang_ru")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛂 Визовый отдел", callback_data="visa_ru"),
             InlineKeyboardButton(text="✈️ Авиакасса", callback_data="aviation_ru")],
            [InlineKeyboardButton(text="📞 Быстрая связь", callback_data="contact_ru"),
             InlineKeyboardButton(text="📍 Адрес", callback_data="address_ru")],
            [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="question_ru")],
            [InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="lang_uz")],
        ])

# ── VIZA ──────────────────────────────────────────────────────

def visa_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Viza javobi", callback_data="visa_answer_uz")],
            [InlineKeyboardButton(text="🏛 O'zb Konsulstvo guruhi", callback_data="visa_consul_uz")],
            [InlineKeyboardButton(text="📝 Anketa to'ldirish", callback_data="visa_anketa_uz")],
            [InlineKeyboardButton(text="🇹🇲 Turkman fuqarolari uchun O'zb viza", callback_data="visa_turkmen_uz")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Ответ по визе", callback_data="visa_answer_ru")],
            [InlineKeyboardButton(text="🏛 Группа Консульства Узб", callback_data="visa_consul_ru")],
            [InlineKeyboardButton(text="📝 Заполнить анкету", callback_data="visa_anketa_ru")],
            [InlineKeyboardButton(text="🇹🇲 Виза Узб для граждан Туркменистана", callback_data="visa_turkmen_ru")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

@dp.callback_query(F.data.startswith("visa_answer_"))
async def visa_answer(callback: CallbackQuery):
    lang = callback.data.split("_")[2]
    if lang == "uz":
        text = (
            "📋 <b>Viza javobi</b>\n\n"
            "O'zbekiston vizangiz holati haqida ma'lumot olish uchun:\n\n"
            "✅ Barcode orqali viza javobingizni tekshirishingiz mumkin.\n\n"
            "👇 Quyidagi tugmani bosing va botga o'ting:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Viza javobini tekshirish", url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="visa_uz")],
        ])
    else:
        text = (
            "📋 <b>Ответ по визе</b>\n\n"
            "Для получения информации о статусе вашей визы в Узбекистан:\n\n"
            "✅ Вы можете проверить ответ по визе через штрихкод.\n\n"
            "👇 Нажмите кнопку ниже:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Проверить ответ по визе", url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="visa_ru")],
        ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("visa_consul_"))
async def visa_consul(callback: CallbackQuery):
    lang = callback.data.split("_")[2]
    if lang == "uz":
        text = (
            "🏛 <b>Sankt-Peterburgdagi O'zbekiston Elchixonasi</b>\n\n"
            "Rasmiy konsullik xizmatlari va ma'lumotlar uchun "
            "O'zbekiston Konsulstvo guruhiga qo'shilishingiz mumkin.\n\n"
            "📌 Guruhda siz quyidagilarni topasiz:\n"
            "• Rasmiy e'lonlar va yangiliklar\n"
            "• Viza va hujjatlar bo'yicha ma'lumotlar\n"
            "• Konsullik qabulxonasi ish vaqti\n\n"
            "👇 Guruhga qo'shilish uchun bosing:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏛 Guruhga qo'shilish", url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="visa_uz")],
        ])
    else:
        text = (
            "🏛 <b>Консульство Узбекистана в Санкт-Петербурге</b>\n\n"
            "Для получения официальной консульской информации "
            "вы можете вступить в группу Консульства Узбекистана.\n\n"
            "📌 В группе вы найдёте:\n"
            "• Официальные объявления и новости\n"
            "• Информацию по визам и документам\n"
            "• Часы работы консульского отдела\n\n"
            "👇 Нажмите для вступления в группу:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏛 Вступить в группу", url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="visa_ru")],
        ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("visa_anketa_"))
async def visa_anketa(callback: CallbackQuery):
    lang = callback.data.split("_")[2]
    if lang == "uz":
        text = (
            "📝 <b>Anketa to'ldirish xizmati</b>\n\n"
            "Viza uchun anketa to'ldirishda yordam kerakmi?\n\n"
            "✅ Bizning mutaxassislarimiz sizga yordam beradi:\n"
            "• Anketani to'g'ri to'ldirish\n"
            "• Hujjatlarni tayyorlash\n"
            "• Ariza topshirish\n\n"
            "👇 Anketa to'ldirish uchun murojaat qiling:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Anketa to'ldirish", url="https://t.me/AVIAKASSA9094")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="visa_uz")],
        ])
    else:
        text = (
            "📝 <b>Услуга заполнения анкеты</b>\n\n"
            "Нужна помощь в заполнении анкеты на визу?\n\n"
            "✅ Наши специалисты помогут вам:\n"
            "• Правильно заполнить анкету\n"
            "• Подготовить документы\n"
            "• Подать заявление\n\n"
            "👇 Обратитесь для заполнения анкеты:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Заполнить анкету", url="https://t.me/AVIAKASSA9094")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="visa_ru")],
        ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("visa_turkmen_"))
async def visa_turkmen(callback: CallbackQuery):
    lang = callback.data.split("_")[2]
    if lang == "uz":
        text = (
            "🇹🇲 <b>Turkmaniston fuqarolari uchun O'zbekiston vizasi</b>\n\n"
            "Biz Turkmaniston fuqarolari uchun O'zbekiston vizasini "
            "rasmiylashtirish bo'yicha to'liq yordam ko'rsatamiz.\n\n"
            "📋 <b>Kerakli hujjatlar:</b>\n"
            "• Pasport (kamida 6 oy amal qilishi kerak)\n"
            "• 2 ta 3×4 rasm\n"
            "• To'ldirilgan anketa\n"
            "• Taklif xati yoki mehmonxona bron\n"
            "• Konsullik to'lovi\n\n"
            "🏛 <b>Sankt-Peterburgdagi O'zbekiston Elchixonasi</b> bilan "
            "bog'lanishingiz mumkin yoki bizga murojaat qiling.\n\n"
            "👇 Bog'lanish uchun bosing:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Bog'lanish", url="https://t.me/OMAD_TOUR9094")],
            [InlineKeyboardButton(text="🏛 Konsulstvo guruhi", url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="visa_uz")],
        ])
    else:
        text = (
            "🇹🇲 <b>Виза Узбекистана для граждан Туркменистана</b>\n\n"
            "Мы оказываем полную помощь гражданам Туркменистана "
            "в оформлении визы в Узбекистан.\n\n"
            "📋 <b>Необходимые документы:</b>\n"
            "• Паспорт (действителен минимум 6 месяцев)\n"
            "• 2 фотографии 3×4\n"
            "• Заполненная анкета\n"
            "• Приглашение или бронь отеля\n"
            "• Консульский сбор\n\n"
            "🏛 Вы можете обратиться в <b>Консульство Узбекистана "
            "в Санкт-Петербурге</b> или к нам напрямую.\n\n"
            "👇 Нажмите для связи:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Связаться", url="https://t.me/OMAD_TOUR9094")],
            [InlineKeyboardButton(text="🏛 Группа консульства", url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="visa_ru")],
        ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── AVIAKASSA ─────────────────────────────────────────────────

def aviation_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094")],
            [InlineKeyboardButton(text="📱 IMO", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="🔵 Max", url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk")],
            [InlineKeyboardButton(text="💰 Narxlarni ko'rish", callback_data="prices_uz")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094")],
            [InlineKeyboardButton(text="📱 IMO", url="https://t.me/OMAD_TOUR9094"),
             InlineKeyboardButton(text="🔵 Max", url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk")],
            [InlineKeyboardButton(text="💰 Посмотреть цены", callback_data="prices_ru")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

# ── TEZKOR ALOQA ──────────────────────────────────────────────

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

# ── MANZIL ────────────────────────────────────────────────────

def address_menu(lang):
    if lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 1-ofis xaritada", url="https://yandex.ru/maps/-/CLaRUCPW")],
            [InlineKeyboardButton(text="🗺 2-ofis xaritada", url="https://yandex.ru/maps/org/omad_tour/50809406614")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Офис 1 на карте", url="https://yandex.ru/maps/-/CLaRUCPW")],
            [InlineKeyboardButton(text="🗺 Офис 2 на карте", url="https://yandex.ru/maps/org/omad_tour/50809406614")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

# ── NARXLAR ───────────────────────────────────────────────────

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

# ── ADMIN ─────────────────────────────────────────────────────

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

# ── VIZA BOSH ─────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("visa_uz"))
async def visa_uz(callback: CallbackQuery):
    if callback.data != "visa_uz":
        return
    text = (
        "🛂 <b>Viza bo'limi</b>\n\n"
        "O'zbekiston vizasi va konsullik xizmatlari bo'yicha "
        "to'liq yordam ko'rsatamiz.\n\n"
        "Kerakli bo'limni tanlang 👇"
    )
    await callback.message.edit_text(text, reply_markup=visa_menu("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "visa_ru")
async def visa_ru(callback: CallbackQuery):
    text = (
        "🛂 <b>Визовый отдел</b>\n\n"
        "Оказываем полную помощь по визам в Узбекистан "
        "и консульским услугам.\n\n"
        "Выберите нужный раздел 👇"
    )
    await callback.message.edit_text(text, reply_markup=visa_menu("ru"), parse_mode="HTML")

# ── AVIAKASSA ─────────────────────────────────────────────────

@dp.callback_query(F.data == "aviation_uz")
async def aviation_uz(callback: CallbackQuery):
    text = (
        "✈️ <b>Aviakassa — ОМАД ТУР</b>\n\n"
        "Санкт-Петербург dan O'zbekistonga\n"
        "eng arzon aviabiletlar!\n\n"
        "🛫 Barcha yo'nalishlar bo'yicha biletlar\n"
        "💼 Bagaj bilan va bagesiz variantlar\n"
        "✅ Rasmiy aviakassa\n\n"
        "Biz bilan bog'laning 👇"
    )
    await callback.message.edit_text(text, reply_markup=aviation_menu("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "aviation_ru")
async def aviation_ru(callback: CallbackQuery):
    text = (
        "✈️ <b>Авиакасса — ОМАД ТУР</b>\n\n"
        "Авиабилеты из Санкт-Петербурга\n"
        "в Узбекистан по самым низким ценам!\n\n"
        "🛫 Билеты по всем направлениям\n"
        "💼 С багажом и без\n"
        "✅ Официальная авиакасса\n\n"
        "Свяжитесь с нами 👇"
    )
    await callback.message.edit_text(text, reply_markup=aviation_menu("ru"), parse_mode="HTML")

# ── NARXLAR ───────────────────────────────────────────────────

@dp.callback_query(F.data == "prices_uz")
async def prices_uz(callback: CallbackQuery):
    await callback.message.edit_text(
        "✈️ <b>Yo'nalishni tanlang:</b>",
        reply_markup=prices_keyboard("uz"), parse_mode="HTML"
    )

@dp.callback_query(F.data == "prices_ru")
async def prices_ru(callback: CallbackQuery):
    await callback.message.edit_text(
        "✈️ <b>Выберите направление:</b>",
        reply_markup=prices_keyboard("ru"), parse_mode="HTML"
    )

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

# ── TEZKOR ALOQA ──────────────────────────────────────────────

@dp.callback_query(F.data == "contact_uz")
async def contact_uz(callback: CallbackQuery):
    text = (
        "📞 <b>Tezkor aloqa</b>\n\n"
        "Istalgan vaqt qo'ng'iroq qiling!\n"
        "Doim yordam berishga tayyormiz 🙏\n\n"
        "👇 Raqamni bosing — qo'ng'iroq ochiladi:"
    )
    await callback.message.edit_text(text, reply_markup=contact_menu("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "contact_ru")
async def contact_ru(callback: CallbackQuery):
    text = (
        "📞 <b>Быстрая связь</b>\n\n"
        "Звоните в любое время!\n"
        "Всегда готовы помочь 🙏\n\n"
        "👇 Нажмите на номер — откроется звонок:"
    )
    await callback.message.edit_text(text, reply_markup=contact_menu("ru"), parse_mode="HTML")

# ── MANZIL ────────────────────────────────────────────────────

@dp.callback_query(F.data == "address_uz")
async def address_uz(callback: CallbackQuery):
    text = (
        "📍 <b>Bizning manzillar</b>\n\n"
        "🏢 <b>ОМАД ТУР</b>\n\n"
        "📌 <b>1-ofis:</b>\n"
        "просп. Большевиков, 24, корп. 1\n\n"
        "📌 <b>2-ofis:</b>\n"
        "ул. 4-я Красноармейская, дом 3\n\n"
        "🕐 Ish vaqti: 09:00 — 21:00 (har kuni)\n\n"
        "👇 Xaritada ko'rish uchun bosing:"
    )
    await callback.message.edit_text(text, reply_markup=address_menu("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "address_ru")
async def address_ru(callback: CallbackQuery):
    text = (
        "📍 <b>Наши адреса</b>\n\n"
        "🏢 <b>ОМАД ТУР</b>\n\n"
        "📌 <b>Офис 1:</b>\n"
        "просп. Большевиков, 24, корп. 1\n\n"
        "📌 <b>Офис 2:</b>\n"
        "ул. 4-я Красноармейская, дом 3\n\n"
        "🕐 Режим работы: 09:00 — 21:00 (ежедневно)\n\n"
        "👇 Нажмите для просмотра на карте:"
    )
    await callback.message.edit_text(text, reply_markup=address_menu("ru"), parse_mode="HTML")

# ── SAVOL ─────────────────────────────────────────────────────

@dp.callback_query(F.data == "question_uz")
async def question_uz(callback: CallbackQuery, state: FSMContext):
    await state.update_data(lang="uz")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")]
    ])
    await callback.message.edit_text(
        "✉️ <b>Savol yuborish</b>\n\n"
        "Savolingizni yozing yoki rasm/fayl yuboring.\n"
        "Tez orada javob beramiz! 🙏",
        reply_markup=kb, parse_mode="HTML"
    )
    await state.set_state(States.waiting_question)

@dp.callback_query(F.data == "question_ru")
async def question_ru(callback: CallbackQuery, state: FSMContext):
    await state.update_data(lang="ru")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")]
    ])
    await callback.message.edit_text(
        "✉️ <b>Задать вопрос</b>\n\n"
        "Напишите ваш вопрос или отправьте фото/файл.\n"
        "Ответим как можно скорее! 🙏",
        reply_markup=kb, parse_mode="HTML"
    )
    await state.set_state(States.waiting_question)

@dp.message(States.waiting_question)
async def receive_question(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user = message.from_user
    username = f"@{user.username}" if user.username else "—"

    header = (
        f"📨 <b>Yangi savol keldi!</b>\n\n"
        f"👤 Ism: <b>{user.full_name}</b>\n"
        f"📱 Telegram: {username}\n"
        f"🆔 ID: <code>{user.id}</code>"
    )
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_{user.id}")]
    ])
    await bot.send_message(ADMIN_ID, header, reply_markup=reply_kb, parse_mode="HTML")

    if message.text:
        await bot.send_message(ADMIN_ID, f"💬 <b>Savol matni:</b>\n\n{message.text}", parse_mode="HTML")
    elif message.photo:
        cap = message.caption or ""
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
                             caption=f"🖼 <b>Rasm bilan savol:</b>\n{cap}", parse_mode="HTML")
    elif message.document:
        cap = message.caption or ""
        await bot.send_document(ADMIN_ID, message.document.file_id,
                                caption=f"📄 <b>Fayl bilan savol:</b>\n{cap}", parse_mode="HTML")
    elif message.video:
        cap = message.caption or ""
        await bot.send_video(ADMIN_ID, message.video.file_id,
                             caption=f"🎥 <b>Video bilan savol:</b>\n{cap}", parse_mode="HTML")
    elif message.voice:
        await bot.send_voice(ADMIN_ID, message.voice.file_id)
        await bot.send_message(ADMIN_ID, "🎤 <b>Ovozli xabar yuborildi</b>", parse_mode="HTML")

    if lang == "uz":
        confirm = "✅ <b>Murojaatingiz qabul qilindi!</b>\n\nIltimos javobni kuting. 🙏"
    else:
        confirm = "✅ <b>Ваш запрос принят!</b>\n\nПожалуйста, ожидайте ответа. 🙏"
    await message.answer(confirm, reply_markup=main_menu(lang), parse_mode="HTML")
    await state.clear()

# ── ADMIN JAVOB ───────────────────────────────────────────────

@dp.callback_query(F.data.startswith("reply_"))
async def reply_to_user(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split("_")[1])
    await state.update_data(reply_to=user_id)
    await callback.message.answer(
        "✏️ Javobingizni yozing (matn, rasm, video yoki fayl):"
    )
    await state.set_state(States.waiting_reply)

@dp.message(States.waiting_reply)
async def send_reply(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    user_id = data.get("reply_to")
    try:
        header = "📬 <b>ОМАД ТУР dan javob:</b>\n\n"
        if message.text:
            await bot.send_message(user_id, header + message.text, parse_mode="HTML")
        elif message.photo:
            cap = header + (message.caption or "")
            await bot.send_photo(user_id, message.photo[-1].file_id, caption=cap, parse_mode="HTML")
        elif message.video:
            cap = header + (message.caption or "")
            await bot.send_video(user_id, message.video.file_id, caption=cap, parse_mode="HTML")
        elif message.document:
            cap = header + (message.caption or "")
            await bot.send_document(user_id, message.document.file_id, caption=cap, parse_mode="HTML")
        elif message.voice:
            await bot.send_voice(user_id, message.voice.file_id)
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
        f"<b>Foydalanuvchilar ro'yxati:</b>\n\n"
    )
    for i, (uid, u) in enumerate(list(users.items())[-20:]):
        uname = f"@{u['username']}" if u.get("username") else "—"
        text += f"{i+1}. {u['full_name']} {uname} — {u['count']} marta\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_back")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer(
        "📢 <b>Reklama yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni yozing.\n"
        "Matn, rasm, video yoki fayl yuborishingiz mumkin:",
        parse_mode="HTML"
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
    await callback.message.edit_text(
        "💰 <b>Narxlar boshqaruvi</b>",
        reply_markup=admin_prices_kb(), parse_mode="HTML"
    )

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
        await message.answer(f"✅ O'chirildi: {direction}", reply_markup=admin_prices_kb())
        await state.clear()
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

# ── MAIN ──────────────────────────────────────────────────────

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
