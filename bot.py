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
ADMIN_ID  = 7359558983
SBOR      = 500
PRICES_F  = "prices.json"
USERS_F   = "users.json"

# ── FAYLLAR ──────────────────────────────────────────────────

DEFAULT_PRICES = {
    "Санкт-Петербург → Ташкент":   18500,
    "Санкт-Петербург → Самарканд": 19500,
    "Санкт-Петербург → Фергана":   20000,
    "Санкт-Петербург → Наманган":  19500,
    "Санкт-Петербург → Андижан":   20000,
    "Санкт-Петербург → Бухара":    21000,
    "Санкт-Петербург → Термез":    22000,
    "Санкт-Петербург → Карши":     22000,
    "Санкт-Петербург → Нукус":     23000,
    "Санкт-Петербург → Ургенч":    23000,
}

def load_prices():
    if os.path.exists(PRICES_F):
        with open(PRICES_F, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict(DEFAULT_PRICES)

def save_prices(data):
    with open(PRICES_F, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists(USERS_F):
        with open(USERS_F, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def register_user(uid, username, full_name):
    users = load_users()
    key = str(uid)
    if key not in users:
        users[key] = {"username": username or "", "full_name": full_name, "visits": 1}
    else:
        users[key]["visits"] += 1
    with open(USERS_F, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ── BOT ──────────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

class S(StatesGroup):
    question      = State()
    reply         = State()
    broadcast     = State()
    add_dir       = State()
    add_price     = State()
    edit_select   = State()
    edit_price    = State()
    delete_select = State()

# ── BOSH MENU ────────────────────────────────────────────────

def kb_main(lang):
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🛂 Viza bo'limi" if uz else "🛂 Визовый отдел",
                callback_data=f"visa_{lang}"
            ),
            InlineKeyboardButton(
                text="✈️ Aviakassa" if uz else "✈️ Авиакасса",
                callback_data=f"avia_{lang}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📞 Tezkor aloqa" if uz else "📞 Быстрая связь",
                callback_data=f"contact_{lang}"
            ),
            InlineKeyboardButton(
                text="📍 Manzil" if uz else "📍 Адрес",
                callback_data=f"address_{lang}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="❓ Savol yuborish" if uz else "❓ Задать вопрос",
                callback_data=f"question_{lang}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🇷🇺 Русский" if uz else "🇺🇿 O'zbek",
                callback_data="lang_ru" if uz else "lang_uz"
            ),
        ],
    ])

def txt_home(lang):
    if lang == "uz":
        return "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\nXush kelibsiz! Bo'limni tanlang 👇"
    return "✈️ <b>ОМАД ТУР</b> — Авиакасса\n\nДобро пожаловать! Выберите раздел 👇"

# ── START / ADMIN ─────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    register_user(msg.from_user.id, msg.from_user.username, msg.from_user.full_name)
    await msg.answer(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")

@dp.message(Command("admin"))
async def cmd_admin(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer(
        "🔧 <b>Admin panel</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika",       callback_data="adm_stats")],
            [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="adm_broadcast")],
            [InlineKeyboardButton(text="💰 Narxlar",          callback_data="adm_prices")],
        ]),
        parse_mode="HTML"
    )

# ── TIL ──────────────────────────────────────────────────────

@dp.callback_query(F.data == "lang_uz")
async def lang_uz(cb: CallbackQuery):
    await cb.message.edit_text(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "lang_ru")
async def lang_ru(cb: CallbackQuery):
    await cb.message.edit_text(txt_home("ru"), reply_markup=kb_main("ru"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("home_"))
async def go_home(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    await cb.message.edit_text(txt_home(lang), reply_markup=kb_main(lang), parse_mode="HTML")

# ── VIZA (birdaniga matn + 2 ta tugma) ───────────────────────

@dp.callback_query(F.data.startswith("visa_"))
async def visa_section(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    uz = lang == "uz"

    if uz:
        text = (
            "🛂 <b>Viza bo'limi</b>\n\n"
            "Biz O'zbekiston vizasi bo'yicha to'liq yordam ko'rsatamiz:\n\n"
            "📋 <b>Viza javobi</b> — barcode orqali viza holatingizni tekshiring\n\n"
            "🏛 <b>O'zb Konsulstvo guruhi</b> — Sankt-Peterburgdagi "
            "O'zbekiston Elchixonasining rasmiy guruhi. "
            "Viza, hujjatlar va konsullik xizmatlari haqida rasmiy ma'lumotlar\n\n"
            "📝 <b>Anketa to'ldirish</b> — viza uchun anketa to'ldirishda "
            "mutaxassislarimiz yordam beradi\n\n"
            "🇹🇲 <b>Turkmaniston fuqarolari uchun O'zbekiston vizasi</b>\n\n"
            "Biz Turkmaniston fuqarolari uchun O'zbekiston vizasini "
            "rasmiylashtirish bo'yicha to'liq yordam ko'rsatamiz.\n\n"
            "🏛 Sankt-Peterburgdagi O'zbekiston Elchixonasi bilan "
            "bog'lanishingiz mumkin yoki bizga murojaat qiling.\n\n"
            "👇 Anketa to'ldirish va bog'lanish uchun kerakli tugmani bosing:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Viza javobini tekshirish",
                                  url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa")],
            [InlineKeyboardButton(text="🏛 O'zb Konsulstvo guruhi",
                                  url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="📝 Anketa to'ldirish",
                                  url="https://t.me/AVIAKASSA9094")],
            [InlineKeyboardButton(text="📞 Bog'lanish",
                                  url="https://t.me/OMAD_TOUR9094")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        text = (
            "🛂 <b>Визовый отдел</b>\n\n"
            "Оказываем полную помощь по визам в Узбекистан:\n\n"
            "📋 <b>Ответ по визе</b> — проверьте статус вашей визы по штрихкоду\n\n"
            "🏛 <b>Группа Консульства Узб</b> — официальная группа "
            "Консульства Узбекистана в Санкт-Петербурге. "
            "Официальная информация по визам, документам и консульским услугам\n\n"
            "📝 <b>Заполнить анкету</b> — наши специалисты помогут "
            "правильно заполнить анкету на визу\n\n"
            "🇹🇲 <b>Виза Узбекистана для граждан Туркменистана</b>\n\n"
            "Оказываем полную помощь гражданам Туркменистана "
            "в оформлении визы в Узбекистан.\n\n"
            "🏛 Можете обратиться в Консульство Узбекистана "
            "в Санкт-Петербурге или к нам напрямую.\n\n"
            "👇 Нажмите нужную кнопку для анкеты или связи:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Проверить ответ по визе",
                                  url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa")],
            [InlineKeyboardButton(text="🏛 Группа Консульства Узб",
                                  url="https://t.me/+i8I6ByH_CUVhOWQy")],
            [InlineKeyboardButton(text="📝 Заполнить анкету",
                                  url="https://t.me/AVIAKASSA9094")],
            [InlineKeyboardButton(text="📞 Связаться",
                                  url="https://t.me/OMAD_TOUR9094")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])

    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── AVIAKASSA ────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("avia_"))
async def avia_section(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    uz = lang == "uz"
    if uz:
        text = (
            "✈️ <b>Aviakassa — ОМАД ТУР</b>\n\n"
            "Санкт-Петербург dan O'zbekistonga\n"
            "eng arzon aviabiletlar!\n\n"
            "🛫 Barcha yo'nalishlar\n"
            "💼 Bagaj bilan va bagesiz\n"
            "✅ Rasmiy aviakassa\n\n"
            "Biz bilan bog'laning 👇"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
                InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094"),
            ],
            [
                InlineKeyboardButton(text="📱 IMO", url="https://t.me/OMAD_TOUR9094"),
                InlineKeyboardButton(text="🔵 Max", url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk"),
            ],
            [InlineKeyboardButton(text="💰 Narxlarni ko'rish", callback_data="prices_uz")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        text = (
            "✈️ <b>Авиакасса — ОМАД ТУР</b>\n\n"
            "Авиабилеты из Санкт-Петербурга\n"
            "в Узбекистан по низким ценам!\n\n"
            "🛫 Все направления\n"
            "💼 С багажом и без\n"
            "✅ Официальная авиакасса\n\n"
            "Свяжитесь с нами 👇"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
                InlineKeyboardButton(text="💚 WhatsApp", url="https://wa.me/79811939094"),
            ],
            [
                InlineKeyboardButton(text="📱 IMO", url="https://t.me/OMAD_TOUR9094"),
                InlineKeyboardButton(text="🔵 Max", url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk"),
            ],
            [InlineKeyboardButton(text="💰 Посмотреть цены", callback_data="prices_ru")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── NARXLAR ──────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("prices_"))
async def prices_section(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    prices = load_prices()
    rows = []
    for i, direction in enumerate(prices):
        rows.append([InlineKeyboardButton(
            text=f"✈️ {direction}",
            callback_data=f"dir_{lang}_{i}"
        )])
    back = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    rows.append([InlineKeyboardButton(text=back, callback_data=f"avia_{lang}")])
    title = "✈️ <b>Yo'nalishni tanlang:</b>" if lang == "uz" else "✈️ <b>Выберите направление:</b>"
    await cb.message.edit_text(title, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@dp.callback_query(F.data.startswith("dir_"))
async def price_detail(cb: CallbackQuery):
    parts = cb.data.split("_")
    lang  = parts[1]
    idx   = int(parts[2])
    prices     = load_prices()
    directions = list(prices.keys())
    if idx >= len(directions):
        await cb.answer("Topilmadi!")
        return
    direction   = directions[idx]
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
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── TEZKOR ALOQA (faqat matn + raqamlar) ─────────────────────

@dp.callback_query(F.data.startswith("contact_"))
async def contact_section(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    uz = lang == "uz"
    if uz:
        text = (
            "📞 <b>Tezkor aloqa</b>\n\n"
            "Istalgan vaqt qo'ng'iroq qiling!\n\n"
            "📱 +7 981 193 90 94\n"
            "📱 +7 937 949 90 94\n"
            "📱 +7 921 402 74 89"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        text = (
            "📞 <b>Быстрая связь</b>\n\n"
            "Звоните в любое время!\n\n"
            "📱 +7 981 193 90 94\n"
            "📱 +7 937 949 90 94\n"
            "📱 +7 921 402 74 89"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── MANZIL ───────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("address_"))
async def address_section(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    uz = lang == "uz"
    if uz:
        text = (
            "📍 <b>Bizning manzillar</b>\n\n"
            "🏢 <b>ОМАД ТУР</b>\n\n"
            "📌 <b>1-ofis (asosiy):</b>\n"
            "Metro: Технологический институт\n"
            "ул. 4-я Красноармейская, дом 3\n"
            "Домофон: 22Б\n\n"
            "📌 <b>2-ofis:</b>\n"
            "просп. Большевиков, 24, корп. 1\n\n"
            "🕐 Ish vaqti: 09:00 — 21:00 (har kuni)\n\n"
            "👇 Xaritada ko'rish uchun bosing:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 1-ofis — 4-я Красноармейская",
                                  url="https://yandex.ru/maps/-/CLaRUCPW")],
            [InlineKeyboardButton(text="🗺 2-ofis — Большевиков",
                                  url="https://yandex.ru/maps/org/omad_tour/50809406614")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="home_uz")],
        ])
    else:
        text = (
            "📍 <b>Наши адреса</b>\n\n"
            "🏢 <b>ОМАД ТУР</b>\n\n"
            "📌 <b>Офис 1 (основной):</b>\n"
            "Метро: Технологический институт\n"
            "ул. 4-я Красноармейская, дом 3\n"
            "Домофон: 22Б\n\n"
            "📌 <b>Офис 2:</b>\n"
            "просп. Большевиков, 24, корп. 1\n\n"
            "🕐 Режим работы: 09:00 — 21:00 (ежедневно)\n\n"
            "👇 Нажмите для просмотра на карте:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Офис 1 — 4-я Красноармейская",
                                  url="https://yandex.ru/maps/-/CLaRUCPW")],
            [InlineKeyboardButton(text="🗺 Офис 2 — Большевиков",
                                  url="https://yandex.ru/maps/org/omad_tour/50809406614")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="home_ru")],
        ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ── SAVOL ────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("question_"))
async def question_section(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await state.update_data(lang=lang)
    uz = lang == "uz"
    await cb.message.edit_text(
        "✉️ <b>Savol yuborish</b>\n\n"
        "Savolingizni yozing yoki\n"
        "rasm / video / fayl / ovoz yuboring.\n\n"
        "Tez orada javob beramiz! 🙏"
        if uz else
        "✉️ <b>Задать вопрос</b>\n\n"
        "Напишите ваш вопрос или\n"
        "отправьте фото / видео / файл / голос.\n\n"
        "Ответим как можно скорее! 🙏",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="⬅️ Ortga" if uz else "⬅️ Назад",
                callback_data=f"home_{lang}"
            )]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(S.question)

@dp.message(S.question)
async def receive_question(msg: Message, state: FSMContext):
    data  = await state.get_data()
    lang  = data.get("lang", "uz")
    user  = msg.from_user
    uname = f"@{user.username}" if user.username else "—"

    header = (
        f"📨 <b>Yangi savol!</b>\n\n"
        f"👤 {user.full_name}\n"
        f"📱 {uname}\n"
        f"🆔 <code>{user.id}</code>"
    )
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_{user.id}")]
    ])
    await bot.send_message(ADMIN_ID, header, reply_markup=reply_kb, parse_mode="HTML")

    if msg.text:
        await bot.send_message(ADMIN_ID, f"💬 <b>Savol:</b>\n\n{msg.text}", parse_mode="HTML")
    elif msg.photo:
        await bot.send_photo(ADMIN_ID, msg.photo[-1].file_id,
                             caption=f"🖼 {msg.caption or ''}")
    elif msg.video:
        await bot.send_video(ADMIN_ID, msg.video.file_id,
                             caption=f"🎥 {msg.caption or ''}")
    elif msg.document:
        await bot.send_document(ADMIN_ID, msg.document.file_id,
                                caption=f"📄 {msg.caption or ''}")
    elif msg.voice:
        await bot.send_voice(ADMIN_ID, msg.voice.file_id)

    confirm = (
        "✅ <b>Murojaatingiz qabul qilindi!</b>\n\nJavobni kuting 🙏"
        if lang == "uz" else
        "✅ <b>Ваш запрос принят!</b>\n\nОжидайте ответа 🙏"
    )
    await msg.answer(confirm, reply_markup=kb_main(lang), parse_mode="HTML")
    await state.clear()

# ── ADMIN JAVOB ──────────────────────────────────────────────

@dp.callback_query(F.data.startswith("reply_"))
async def start_reply(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    uid = int(cb.data.split("_")[1])
    await state.update_data(reply_to=uid)
    await cb.message.answer("✏️ Javobingizni yozing (matn, rasm, video, fayl yoki ovoz):")
    await state.set_state(S.reply)

@dp.message(S.reply)
async def send_reply(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    uid  = data.get("reply_to")
    head = "📬 <b>ОМАД ТУР dan javob:</b>\n\n"
    try:
        if msg.text:
            await bot.send_message(uid, head + msg.text, parse_mode="HTML")
        elif msg.photo:
            await bot.send_photo(uid, msg.photo[-1].file_id,
                                 caption=head + (msg.caption or ""), parse_mode="HTML")
        elif msg.video:
            await bot.send_video(uid, msg.video.file_id,
                                 caption=head + (msg.caption or ""), parse_mode="HTML")
        elif msg.document:
            await bot.send_document(uid, msg.document.file_id,
                                    caption=head + (msg.caption or ""), parse_mode="HTML")
        elif msg.voice:
            await bot.send_voice(uid, msg.voice.file_id)
        await msg.answer("✅ Javob yuborildi!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")]
        ]))
    except Exception as e:
        await msg.answer(f"❌ Xato: {e}")
    await state.clear()

# ── ADMIN PANEL ──────────────────────────────────────────────

def kb_admin_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika",       callback_data="adm_stats")],
        [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="💰 Narxlar",          callback_data="adm_prices")],
    ])

def kb_admin_prices():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Qo'shish",     callback_data="adm_add"),
            InlineKeyboardButton(text="✏️ O'zgartirish", callback_data="adm_edit"),
        ],
        [
            InlineKeyboardButton(text="🗑 O'chirish",    callback_data="adm_delete"),
            InlineKeyboardButton(text="📋 Ro'yxat",      callback_data="adm_list"),
        ],
        [InlineKeyboardButton(text="⬅️ Ortga",           callback_data="adm_main")],
    ])

@dp.callback_query(F.data == "adm_main")
async def adm_main(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text("🔧 <b>Admin panel</b>", reply_markup=kb_admin_main(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_stats")
async def adm_stats(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    users  = load_users()
    total  = len(users)
    visits = sum(u["visits"] for u in users.values())
    lines  = [
        f"📊 <b>Statistika</b>\n",
        f"👥 Foydalanuvchilar: <b>{total}</b>",
        f"🔢 Jami tashriflar: <b>{visits}</b>\n",
        "<b>Ro'yxat:</b>"
    ]
    for i, (_, u) in enumerate(list(users.items())[-20:], 1):
        uname = f"@{u['username']}" if u.get("username") else "—"
        lines.append(f"{i}. {u['full_name']} {uname} — {u['visits']}x")
    await cb.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_main")]
        ]),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.answer(
        "📢 <b>Reklama yuborish</b>\n\n"
        "Xabarni yozing (matn, rasm, video yoki fayl):",
        parse_mode="HTML"
    )
    await state.set_state(S.broadcast)

@dp.message(S.broadcast)
async def do_broadcast(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    users = load_users()
    ok = fail = 0
    for uid in users:
        try:
            if msg.text:
                await bot.send_message(int(uid), msg.text)
            elif msg.photo:
                await bot.send_photo(int(uid), msg.photo[-1].file_id, caption=msg.caption or "")
            elif msg.video:
                await bot.send_video(int(uid), msg.video.file_id, caption=msg.caption or "")
            elif msg.document:
                await bot.send_document(int(uid), msg.document.file_id, caption=msg.caption or "")
            ok += 1
        except:
            fail += 1
    await msg.answer(
        f"✅ Yuborildi: <b>{ok}</b>\n❌ Xato: <b>{fail}</b>",
        reply_markup=kb_admin_main(), parse_mode="HTML"
    )
    await state.clear()

@dp.callback_query(F.data == "adm_prices")
async def adm_prices(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text("💰 <b>Narxlar</b>", reply_markup=kb_admin_prices(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_list")
async def adm_list(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["📋 <b>Narxlar:</b>\n"]
    for i, (d, p) in enumerate(prices.items(), 1):
        lines.append(f"{i}. {d}\n   {p:,} ₽ → mijoz: {p+SBOR:,} ₽\n")
    await cb.message.edit_text("\n".join(lines), reply_markup=kb_admin_prices(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_add")
async def adm_add(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.answer(
        "➕ Yo'nalish nomini yozing:\n<i>Масalan: Санкт-Петербург → Навои</i>",
        parse_mode="HTML"
    )
    await state.set_state(S.add_dir)

@dp.message(S.add_dir)
async def adm_add_dir(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    await state.update_data(direction=msg.text)
    await msg.answer(f"✅ <b>{msg.text}</b>\n\nNarxni kiriting (sborsiz):", parse_mode="HTML")
    await state.set_state(S.add_price)

@dp.message(S.add_price)
async def adm_add_price(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        price = int(msg.text.replace(" ", "").replace(",", ""))
        data  = await state.get_data()
        d     = data["direction"]
        p     = load_prices()
        p[d]  = price
        save_prices(p)
        await msg.answer(
            f"✅ Saqlandi!\n📍 {d}\n💰 {price:,} ₽ → mijoz: {price+SBOR:,} ₽",
            reply_markup=kb_admin_prices(), parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await msg.answer("❌ Faqat raqam! Masalan: 18500")

@dp.callback_query(F.data == "adm_edit")
async def adm_edit(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["✏️ Qaysi raqam? Yozing:\n"]
    for i, (d, p) in enumerate(prices.items(), 1):
        lines.append(f"{i}. {d} — {p:,} ₽")
    await cb.message.answer("\n".join(lines))
    await state.set_state(S.edit_select)

@dp.message(S.edit_select)
async def adm_edit_sel(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        idx = int(msg.text.strip()) - 1
        dirs = list(load_prices().keys())
        if not (0 <= idx < len(dirs)):
            await msg.answer("❌ Noto'g'ri raqam!")
            return
        await state.update_data(direction=dirs[idx])
        await msg.answer(f"✏️ <b>{dirs[idx]}</b>\n\nYangi narx (sborsiz):", parse_mode="HTML")
        await state.set_state(S.edit_price)
    except ValueError:
        await msg.answer("❌ Raqam kiriting!")

@dp.message(S.edit_price)
async def adm_edit_price(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        price = int(msg.text.replace(" ", "").replace(",", ""))
        data  = await state.get_data()
        d     = data["direction"]
        p     = load_prices()
        p[d]  = price
        save_prices(p)
        await msg.answer(
            f"✅ {d}\n💰 {price:,} ₽ → {price+SBOR:,} ₽",
            reply_markup=kb_admin_prices(), parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await msg.answer("❌ Raqam kiriting!")

@dp.callback_query(F.data == "adm_delete")
async def adm_delete(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["🗑 Qaysi raqam? Yozing:\n"]
    for i, (d, p) in enumerate(prices.items(), 1):
        lines.append(f"{i}. {d} — {p:,} ₽")
    await cb.message.answer("\n".join(lines))
    await state.set_state(S.delete_select)

@dp.message(S.delete_select)
async def adm_del_sel(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        idx  = int(msg.text.strip()) - 1
        p    = load_prices()
        dirs = list(p.keys())
        if not (0 <= idx < len(dirs)):
            await msg.answer("❌ Noto'g'ri raqam!")
            return
        d = dirs[idx]
        del p[d]
        save_prices(p)
        await msg.answer(f"✅ O'chirildi: {d}", reply_markup=kb_admin_prices())
        await state.clear()
    except ValueError:
        await msg.answer("❌ Raqam kiriting!")

# ── MAIN ─────────────────────────────────────────────────────

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
