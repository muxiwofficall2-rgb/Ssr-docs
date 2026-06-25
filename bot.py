import asyncio
import logging
import json
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8949050831:AAHqp6G4hmoiAfYvf095_KN3GjTvIdFtWwY"
ADMIN_IDS = [7359558983]
SBOR = 500

DATA_FILE = "prices.json"

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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdminStates(StatesGroup):
    waiting_direction = State()
    waiting_price = State()
    waiting_delete = State()

def main_menu_uz():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Narxlar", callback_data="prices_uz"),
         InlineKeyboardButton(text="📞 Bog'lanish", callback_data="contact_uz")],
        [InlineKeyboardButton(text="ℹ️ Biz haqimizda", callback_data="about_uz"),
         InlineKeyboardButton(text="🌍 Til / Язык", callback_data="lang")],
    ])

def main_menu_ru():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Цены", callback_data="prices_ru"),
         InlineKeyboardButton(text="📞 Контакты", callback_data="contact_ru")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about_ru"),
         InlineKeyboardButton(text="🌍 Til / Язык", callback_data="lang")],
    ])

def lang_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="set_lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")],
    ])

def back_btn(lang):
    text = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"back_{lang}")]
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
    buttons.append([InlineKeyboardButton(text=back_text, callback_data=f"back_{lang}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yo'nalish qo'shish", callback_data="admin_add")],
        [InlineKeyboardButton(text="✏️ Narx o'zgartirish", callback_data="admin_edit")],
        [InlineKeyboardButton(text="🗑 Yo'nalish o'chirish", callback_data="admin_delete")],
        [InlineKeyboardButton(text="📋 Barcha narxlar", callback_data="admin_list")],
    ])

@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\n"
        "🇺🇿 Xush kelibsiz! Tilni tanlang:\n"
        "🇷🇺 Добро пожаловать! Выберите язык:"
    )
    await message.answer(text, reply_markup=lang_menu(), parse_mode="HTML")

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Ruxsat yo'q!")
        return
    await message.answer("🔧 <b>Admin panel</b>", reply_markup=admin_menu(), parse_mode="HTML")

@dp.callback_query(F.data == "lang")
async def show_lang(callback: CallbackQuery):
    await callback.message.edit_text("🌍 Tilni tanlang / Выберите язык:", reply_markup=lang_menu())

@dp.callback_query(F.data == "set_lang_uz")
async def set_uz(callback: CallbackQuery):
    text = (
        "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\n"
        "Санкт-Петербург dan O'zbekistonga arzon aviabiletlar!\n\n"
        "Kerakli bo'limni tanlang 👇"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_uz(), parse_mode="HTML")

@dp.callback_query(F.data == "set_lang_ru")
async def set_ru(callback: CallbackQuery):
    text = (
        "✈️ <b>ОМАД ТУР</b> — Авиакасса\n\n"
        "Авиабилеты из Санкт-Петербурга в Узбекистан!\n\n"
        "Выберите раздел 👇"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_ru(), parse_mode="HTML")

@dp.callback_query(F.data == "back_uz")
async def back_uz(callback: CallbackQuery):
    await set_uz(callback)

@dp.callback_query(F.data == "back_ru")
async def back_ru(callback: CallbackQuery):
    await set_ru(callback)

@dp.callback_query(F.data == "prices_uz")
async def prices_uz(callback: CallbackQuery):
    await callback.message.edit_text(
        "✈️ <b>Yo'nalishni tanlang:</b>",
        reply_markup=prices_keyboard("uz"),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "prices_ru")
async def prices_ru(callback: CallbackQuery):
    await callback.message.edit_text(
        "✈️ <b>Выберите направление:</b>",
        reply_markup=prices_keyboard("ru"),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("dir_"))
async def show_direction(callback: CallbackQuery):
    parts = callback.data.split("_")
    lang = parts[1]
    idx = int(parts[2])
    prices = load_prices()
    directions = list(prices.keys())

    if idx >= len(directions):
        await callback.answer("Yo'nalish topilmadi!")
        return

    direction = directions[idx]
    base_price = prices[direction]
    final_price = base_price + SBOR

    if lang == "uz":
        text = (
            f"✈️ <b>{direction}</b>\n\n"
            f"💰 Narx: <b>{final_price:,} ₽</b>\n\n"
            f"📌 Narxga bagaj va xizmat to'lovlari kiradi\n"
            f"📅 Narxlar har kuni o'zgarishi mumkin\n\n"
            f"🎫 Bilet buyurtma qilish uchun:\n"
            f"👇 Quyidagi tugmani bosing"
        )
        book_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📲 Buyurtma qilish",
                url=f"https://t.me/OMAD_TOUR9094"
            )],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="prices_uz")],
        ])
    else:
        text = (
            f"✈️ <b>{direction}</b>\n\n"
            f"💰 Цена: <b>{final_price:,} ₽</b>\n\n"
            f"📌 В цену включён багаж и сборы\n"
            f"📅 Цены могут меняться ежедневно\n\n"
            f"🎫 Для заказа билета:\n"
            f"👇 Нажмите кнопку ниже"
        )
        book_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📲 Заказать билет",
                url=f"https://t.me/OMAD_TOUR9094"
            )],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="prices_ru")],
        ])

    await callback.message.edit_text(text, reply_markup=book_btn, parse_mode="HTML")

@dp.callback_query(F.data == "contact_uz")
async def contact_uz(callback: CallbackQuery):
    text = (
        "📞 <b>Biz bilan bog'laning:</b>\n\n"
        "📱 Telefon: <b>+7 981 193 90 94</b>\n"
        "💬 Telegram: @OMAD_TOUR9094\n"
        "💚 WhatsApp: +7 981 193 90 94\n\n"
        "📍 Manzil:\nул. 4-я Красноармейская, дом 3\nСанкт-Петербург\n\n"
        "🕐 Ish vaqti: 09:00 — 21:00 (har kuni)"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
         InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_uz")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "contact_ru")
async def contact_ru(callback: CallbackQuery):
    text = (
        "📞 <b>Свяжитесь с нами:</b>\n\n"
        "📱 Телефон: <b>+7 981 193 90 94</b>\n"
        "💬 Telegram: @OMAD_TOUR9094\n"
        "💚 WhatsApp: +7 981 193 90 94\n\n"
        "📍 Адрес:\nул. 4-я Красноармейская, дом 3\nСанкт-Петербург\n\n"
        "🕐 Режим работы: 09:00 — 21:00 (ежедневно)"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
         InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_ru")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "about_uz")
async def about_uz(callback: CallbackQuery):
    text = (
        "ℹ️ <b>ОМАД ТУР haqida</b>\n\n"
        "✈️ Biz Санкт-Петербург dan O'zbekistonga\n"
        "eng arzon aviabiletlarni taklif etamiz!\n\n"
        "🏆 Nima uchun biz?\n"
        "• 10+ yil tajriba\n"
        "• Rasmiy aviakassa\n"
        "• Barcha aviakompaniyalar bilan ishlaymiz\n"
        "• Tez va ishonchli xizmat\n"
        "• O'zbek tilida yordam\n\n"
        "✈️ Aeroflot | Uzbekistan Airways |\n"
        "Qanot Sharq | Somon Air | Pobeda"
    )
    await callback.message.edit_text(text, reply_markup=back_btn("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "about_ru")
async def about_ru(callback: CallbackQuery):
    text = (
        "ℹ️ <b>Об ОМАД ТУР</b>\n\n"
        "✈️ Мы предлагаем самые дешёвые авиабилеты\n"
        "из Санкт-Петербурга в Узбекистан!\n\n"
        "🏆 Почему мы?\n"
        "• Опыт 10+ лет\n"
        "• Официальная авиакасса\n"
        "• Работаем со всеми авиакомпаниями\n"
        "• Быстрый и надёжный сервис\n"
        "• Помощь на узбекском и русском языках\n\n"
        "✈️ Aeroflot | Uzbekistan Airways |\n"
        "Qanot Sharq | Somon Air | Pobeda"
    )
    await callback.message.edit_text(text, reply_markup=back_btn("ru"), parse_mode="HTML")

# ADMIN PANEL
@dp.callback_query(F.data == "admin_list")
async def admin_list(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    prices = load_prices()
    text = "📋 <b>Joriy narxlar (sborsiz):</b>\n\n"
    for i, (d, p) in enumerate(prices.items()):
        text += f"{i+1}. {d}\n   💰 {p:,} ₽ → mijoz: {p+SBOR:,} ₽\n\n"
    await callback.message.edit_text(text, reply_markup=admin_menu(), parse_mode="HTML")

@dp.callback_query(F.data == "admin_add")
async def admin_add(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "➕ Yangi yo'nalish nomini yozing:\n\n<i>Masalan: Санкт-Петербург → Навои</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_direction)

@dp.message(AdminStates.waiting_direction)
async def get_direction(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.update_data(direction=message.text)
    await message.answer(
        f"✅ Yo'nalish: <b>{message.text}</b>\n\nNarxni kiriting (faqat raqam):\n<i>Masalan: 18500</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_price)

@dp.message(AdminStates.waiting_price)
async def get_price(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
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
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting! Masalan: 18500")

@dp.callback_query(F.data == "admin_edit")
async def admin_edit(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    prices = load_prices()
    text = "✏️ Qaysi yo'nalishni o'zgartirish? Raqamini yozing:\n\n"
    for i, (d, p) in enumerate(prices.items()):
        text += f"{i+1}. {d} — {p:,} ₽\n"
    await callback.message.edit_text(text)
    await state.set_state(AdminStates.waiting_delete)
    await state.update_data(mode="edit")

@dp.callback_query(F.data == "admin_delete")
async def admin_delete(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    prices = load_prices()
    text = "🗑 Qaysi yo'nalishni o'chirish? Raqamini yozing:\n\n"
    for i, (d, p) in enumerate(prices.items()):
        text += f"{i+1}. {d} — {p:,} ₽\n"
    await callback.message.edit_text(text)
    await state.set_state(AdminStates.waiting_delete)
    await state.update_data(mode="delete")

@dp.message(AdminStates.waiting_delete)
async def process_delete_edit(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    data = await state.get_data()
    mode = data.get("mode", "delete")
    try:
        idx = int(message.text.strip()) - 1
        prices = load_prices()
        directions = list(prices.keys())
        if idx < 0 or idx >= len(directions):
            await message.answer("❌ Noto'g'ri raqam!")
            return
        direction = directions[idx]
        if mode == "delete":
            del prices[direction]
            save_prices(prices)
            await message.answer(f"✅ O'chirildi: {direction}", reply_markup=admin_menu())
            await state.clear()
        else:
            await state.update_data(direction=direction)
            await message.answer(f"✏️ <b>{direction}</b>\n\nYangi narxni kiriting:", parse_mode="HTML")
            await state.set_state(AdminStates.waiting_price)
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
