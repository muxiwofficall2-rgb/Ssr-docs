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
CONTENT_F = "content.json"

# ═══════════════════════════════════════════════════════════════
#  DEFAULT KONTENT
# ═══════════════════════════════════════════════════════════════
DEFAULT_CONTENT = {
    "visa": {
        "uz": {
            "text": (
                "🛂 <b>Viza bo'limi</b>\n\n"
                "Biz O'zbekiston vizasi bo'yicha to'liq yordam ko'rsatamiz:\n\n"
                "📋 <b>Viza javobi</b> — barcode orqali viza holatingizni tekshiring\n\n"
                "🏛 <b>O'zb Konsulstvo guruhi</b> — Sankt-Peterburgdagi "
                "O'zbekiston Elchixonasining rasmiy guruhi\n\n"
                "📝 <b>Anketa to'ldirish</b> — mutaxassislarimiz yordam beradi\n\n"
                "🇹🇲 <b>Turkmaniston fuqarolari uchun O'zbekiston vizasi</b>\n\n"
                "Biz to'liq yordam ko'rsatamiz. "
                "🏛 Sankt-Peterburgdagi Elchixona bilan bog'lanishingiz mumkin.\n\n"
                "👇 Kerakli tugmani bosing:"
            ),
            "buttons": [
                {"text": "📋 Viza javobini tekshirish", "url": "https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa"},
                {"text": "🏛 O'zb Konsulstvo guruhi",   "url": "https://t.me/+i8I6ByH_CUVhOWQy"},
                {"text": "📝 Anketa to'ldirish",         "url": "https://t.me/AVIAKASSA9094"},
                {"text": "📞 Bog'lanish",                "url": "https://t.me/OMAD_TOUR9094"},
            ]
        },
        "ru": {
            "text": (
                "🛂 <b>Визовый отдел</b>\n\n"
                "Оказываем полную помощь по визам в Узбекистан:\n\n"
                "📋 <b>Ответ по визе</b> — проверьте статус по штрихкоду\n\n"
                "🏛 <b>Группа Консульства Узб</b> — официальная группа "
                "Консульства Узбекистана в Санкт-Петербурге\n\n"
                "📝 <b>Заполнить анкету</b> — наши специалисты помогут\n\n"
                "🇹🇲 <b>Виза Узб для граждан Туркменистана</b>\n\n"
                "Оказываем полную помощь. "
                "🏛 Можете обратиться в Консульство или к нам.\n\n"
                "👇 Нажмите нужную кнопку:"
            ),
            "buttons": [
                {"text": "📋 Проверить ответ по визе", "url": "https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa"},
                {"text": "🏛 Группа Консульства Узб",  "url": "https://t.me/+i8I6ByH_CUVhOWQy"},
                {"text": "📝 Заполнить анкету",         "url": "https://t.me/AVIAKASSA9094"},
                {"text": "📞 Связаться",                "url": "https://t.me/OMAD_TOUR9094"},
            ]
        }
    },
    "avia": {
        "uz": {
            "text": (
                "✈️ <b>Aviakassa — ОМАД ТУР</b>\n\n"
                "Санкт-Петербург dan O'zbekistonga\n"
                "eng arzon aviabiletlar!\n\n"
                "🛫 Barcha yo'nalishlar\n"
                "💼 Bagaj bilan va bagesiz\n"
                "✅ Rasmiy aviakassa\n\n"
                "Biz bilan bog'laning 👇"
            ),
            "buttons": [
                {"text": "💬 Telegram", "url": "https://t.me/OMAD_TOUR9094"},
                {"text": "💚 WhatsApp", "url": "https://wa.me/79811939094"},
                {"text": "📱 IMO",      "url": "https://t.me/OMAD_TOUR9094"},
                {"text": "🔵 Max",      "url": "https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk"},
            ]
        },
        "ru": {
            "text": (
                "✈️ <b>Авиакасса — ОМАД ТУР</b>\n\n"
                "Авиабилеты из Санкт-Петербурга\n"
                "в Узбекистан по низким ценам!\n\n"
                "🛫 Все направления\n"
                "💼 С багажом и без\n"
                "✅ Официальная авиакасса\n\n"
                "Свяжитесь с нами 👇"
            ),
            "buttons": [
                {"text": "💬 Telegram", "url": "https://t.me/OMAD_TOUR9094"},
                {"text": "💚 WhatsApp", "url": "https://wa.me/79811939094"},
                {"text": "📱 IMO",      "url": "https://t.me/OMAD_TOUR9094"},
                {"text": "🔵 Max",      "url": "https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk"},
            ]
        }
    },
    "contact": {
        "uz": {
            "text": (
                "📞 <b>Tezkor aloqa</b>\n\n"
                "Istalgan vaqt qo'ng'iroq qiling!\n\n"
                "📱 +7 981 193 90 94\n"
                "📱 +7 937 949 90 94\n"
                "📱 +7 921 402 74 89"
            ),
            "buttons": []
        },
        "ru": {
            "text": (
                "📞 <b>Быстрая связь</b>\n\n"
                "Звоните в любое время!\n\n"
                "📱 +7 981 193 90 94\n"
                "📱 +7 937 949 90 94\n"
                "📱 +7 921 402 74 89"
            ),
            "buttons": []
        }
    },
    "address": {
        "uz": {
            "text": (
                "📍 <b>Bizning manzillar</b>\n\n"
                "🏢 <b>ОМАД ТУР</b>\n\n"
                "📌 <b>1-ofis (asosiy):</b>\n"
                "Metro: Технологический институт\n"
                "ул. 4-я Красноармейская, дом 3\n"
                "Домофон: 22Б\n\n"
                "📌 <b>2-ofis:</b>\n"
                "просп. Большевиков, 24, корп. 1\n\n"
                "🕐 Ish vaqti: 09:00 — 21:00 (har kuni)"
            ),
            "buttons": [
                {"text": "🗺 1-ofis xaritada", "url": "https://yandex.ru/maps/-/CLaRUCPW"},
                {"text": "🗺 2-ofis xaritada", "url": "https://yandex.ru/maps/org/omad_tour/50809406614"},
            ]
        },
        "ru": {
            "text": (
                "📍 <b>Наши адреса</b>\n\n"
                "🏢 <b>ОМАД ТУР</b>\n\n"
                "📌 <b>Офис 1 (основной):</b>\n"
                "Метро: Технологический институт\n"
                "ул. 4-я Красноармейская, дом 3\n"
                "Домофон: 22Б\n\n"
                "📌 <b>Офис 2:</b>\n"
                "просп. Большевиков, 24, корп. 1\n\n"
                "🕐 Режим работы: 09:00 — 21:00 (ежедневно)"
            ),
            "buttons": [
                {"text": "🗺 Офис 1 на карте", "url": "https://yandex.ru/maps/-/CLaRUCPW"},
                {"text": "🗺 Офис 2 на карте", "url": "https://yandex.ru/maps/org/omad_tour/50809406614"},
            ]
        }
    }
}

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

# ═══════════════════════════════════════════════════════════════
#  FAYL OPERATSIYALARI
# ═══════════════════════════════════════════════════════════════
def load_content():
    if os.path.exists(CONTENT_F):
        with open(CONTENT_F, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(json.dumps(DEFAULT_CONTENT))

def save_content(data):
    with open(CONTENT_F, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

# ═══════════════════════════════════════════════════════════════
#  BOT
# ═══════════════════════════════════════════════════════════════
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

class S(StatesGroup):
    # Foydalanuvchi
    question       = State()
    reply          = State()
    broadcast      = State()
    # CMS — matn
    cms_text       = State()
    # CMS — tugma
    cms_btn_text   = State()
    cms_btn_url    = State()
    # Narx
    add_dir        = State()
    add_price      = State()
    edit_select    = State()
    edit_price     = State()
    delete_select  = State()

# ═══════════════════════════════════════════════════════════════
#  SECTION KLAVIATURASI (dinamik)
# ═══════════════════════════════════════════════════════════════
def kb_section(section: str, lang: str, back_cb: str) -> InlineKeyboardMarkup:
    content = load_content()
    sec = content.get(section, {}).get(lang, {})
    buttons = sec.get("buttons", [])
    rows = []
    for btn in buttons:
        rows.append([InlineKeyboardButton(text=btn["text"], url=btn["url"])])
    # Narxlar tugmasi faqat avia uchun
    if section == "avia":
        rows.append([InlineKeyboardButton(
            text="💰 Narxlarni ko'rish" if lang == "uz" else "💰 Посмотреть цены",
            callback_data=f"prices_{lang}"
        )])
    rows.append([InlineKeyboardButton(
        text="⬅️ Ortga" if lang == "uz" else "⬅️ Назад",
        callback_data=back_cb
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ═══════════════════════════════════════════════════════════════
#  BOSH MENU
# ═══════════════════════════════════════════════════════════════
def kb_main(lang):
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛂 Viza bo'limi" if uz else "🛂 Визовый отдел", callback_data=f"sec_visa_{lang}"),
            InlineKeyboardButton(text="✈️ Aviakassa"    if uz else "✈️ Авиакасса",     callback_data=f"sec_avia_{lang}"),
        ],
        [
            InlineKeyboardButton(text="📞 Tezkor aloqa" if uz else "📞 Быстрая связь", callback_data=f"sec_contact_{lang}"),
            InlineKeyboardButton(text="📍 Manzil"        if uz else "📍 Адрес",          callback_data=f"sec_address_{lang}"),
        ],
        [InlineKeyboardButton(text="❓ Savol yuborish" if uz else "❓ Задать вопрос", callback_data=f"question_{lang}")],
        [InlineKeyboardButton(text="🇷🇺 Русский" if uz else "🇺🇿 O'zbek", callback_data="lang_ru" if uz else "lang_uz")],
    ])

def txt_home(lang):
    if lang == "uz":
        return "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\nXush kelibsiz! Bo'limni tanlang 👇"
    return "✈️ <b>ОМАД ТУР</b> — Авиакасса\n\nДобро пожаловать! Выберите раздел 👇"

# ═══════════════════════════════════════════════════════════════
#  COMMANDS
# ═══════════════════════════════════════════════════════════════
@dp.message(Command("start"))
async def cmd_start(msg: Message):
    register_user(msg.from_user.id, msg.from_user.username, msg.from_user.full_name)
    await msg.answer(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")

@dp.message(Command("admin"))
async def cmd_admin(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("🔧 <b>Admin panel</b>", reply_markup=kb_admin_main(), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  TIL / HOME
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "lang_uz")
async def set_lang_uz(cb: CallbackQuery):
    await cb.message.edit_text(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "lang_ru")
async def set_lang_ru(cb: CallbackQuery):
    await cb.message.edit_text(txt_home("ru"), reply_markup=kb_main("ru"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("home_"))
async def go_home(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    await cb.message.edit_text(txt_home(lang), reply_markup=kb_main(lang), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  BO'LIMLAR (dinamik kontent)
# ═══════════════════════════════════════════════════════════════
SECTION_MAP = {"visa": "visa", "avia": "avia", "contact": "contact", "address": "address"}

@dp.callback_query(F.data.startswith("sec_"))
async def show_section(cb: CallbackQuery):
    parts   = cb.data.split("_")   # sec_visa_uz => ['sec','visa','uz']
    section = parts[1]
    lang    = parts[2]
    content = load_content()
    sec     = content.get(section, {}).get(lang, {})
    text    = sec.get("text", "...")
    kb      = kb_section(section, lang, f"home_{lang}")

    if cb.message.photo:
        await cb.message.delete()
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except:
            await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  NARXLAR
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("prices_"))
async def prices_section(cb: CallbackQuery):
    lang   = cb.data.split("_")[1]
    prices = load_prices()
    rows   = []
    for i, d in enumerate(prices):
        rows.append([InlineKeyboardButton(text=f"✈️ {d}", callback_data=f"dir_{lang}_{i}")])
    back = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    rows.append([InlineKeyboardButton(text=back, callback_data=f"sec_avia_{lang}")])
    title = "✈️ <b>Yo'nalishni tanlang:</b>" if lang == "uz" else "✈️ <b>Выберите направление:</b>"
    await cb.message.edit_text(title, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@dp.callback_query(F.data.startswith("dir_"))
async def price_detail(cb: CallbackQuery):
    parts = cb.data.split("_")
    lang  = parts[1]
    idx   = int(parts[2])
    prices = load_prices()
    dirs   = list(prices.keys())
    if idx >= len(dirs):
        await cb.answer("Topilmadi!")
        return
    d     = dirs[idx]
    final = prices[d] + SBOR
    if lang == "uz":
        text = (
            f"✈️ <b>{d}</b>\n\n"
            f"💰 Narx: <b>{final:,} ₽</b>\n\n"
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
            f"✈️ <b>{d}</b>\n\n"
            f"💰 Цена: <b>{final:,} ₽</b>\n\n"
            f"📌 В цену включён багаж и сборы\n"
            f"📅 Цены могут меняться ежедневно\n\n"
            f"Для заказа 👇"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📲 Заказать билет", url="https://t.me/OMAD_TOUR9094")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="prices_ru")],
        ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  SAVOL
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("question_"))
async def question_section(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await state.update_data(lang=lang)
    uz = lang == "uz"
    await cb.message.edit_text(
        "✉️ <b>Savol yuborish</b>\n\nSavolingizni yozing yoki rasm/video/fayl/ovoz yuboring.\n\nTez orada javob beramiz! 🙏"
        if uz else
        "✉️ <b>Задать вопрос</b>\n\nНапишите вопрос или отправьте фото/видео/файл/голос.\n\nОтветим как можно скорее! 🙏",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Ortga" if uz else "⬅️ Назад", callback_data=f"home_{lang}")]
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
        await bot.send_photo(ADMIN_ID, msg.photo[-1].file_id, caption=f"🖼 {msg.caption or ''}")
    elif msg.video:
        await bot.send_video(ADMIN_ID, msg.video.file_id, caption=f"🎥 {msg.caption or ''}")
    elif msg.document:
        await bot.send_document(ADMIN_ID, msg.document.file_id, caption=f"📄 {msg.caption or ''}")
    elif msg.voice:
        await bot.send_voice(ADMIN_ID, msg.voice.file_id)
    confirm = (
        "✅ <b>Murojaatingiz qabul qilindi!</b>\n\nJavobni kuting 🙏"
        if lang == "uz" else
        "✅ <b>Ваш запрос принят!</b>\n\nОжидайте ответа 🙏"
    )
    await msg.answer(confirm, reply_markup=kb_main(lang), parse_mode="HTML")
    await state.clear()

@dp.callback_query(F.data.startswith("reply_"))
async def start_reply(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    uid = int(cb.data.split("_")[1])
    await state.update_data(reply_to=uid)
    await cb.message.answer("✏️ Javobingizni yozing:")
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
            await bot.send_photo(uid, msg.photo[-1].file_id, caption=head + (msg.caption or ""), parse_mode="HTML")
        elif msg.video:
            await bot.send_video(uid, msg.video.file_id, caption=head + (msg.caption or ""), parse_mode="HTML")
        elif msg.document:
            await bot.send_document(uid, msg.document.file_id, caption=head + (msg.caption or ""), parse_mode="HTML")
        elif msg.voice:
            await bot.send_voice(uid, msg.voice.file_id)
        await msg.answer("✅ Javob yuborildi!", reply_markup=kb_admin_main())
    except Exception as e:
        await msg.answer(f"❌ Xato: {e}")
    await state.clear()

# ═══════════════════════════════════════════════════════════════
#  ADMIN PANEL — ASOSIY
# ═══════════════════════════════════════════════════════════════
def kb_admin_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Kontent boshqaruvi", callback_data="cms_main")],
        [InlineKeyboardButton(text="💰 Narxlar",            callback_data="adm_prices")],
        [InlineKeyboardButton(text="📊 Statistika",         callback_data="adm_stats")],
        [InlineKeyboardButton(text="📢 Reklama yuborish",   callback_data="adm_broadcast")],
    ])

@dp.callback_query(F.data == "adm_main")
async def adm_main(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text("🔧 <b>Admin panel</b>", reply_markup=kb_admin_main(), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  CMS — KONTENT BOSHQARUVI
# ═══════════════════════════════════════════════════════════════
def kb_cms_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛂 Viza",      callback_data="cms_sec_visa"),
            InlineKeyboardButton(text="✈️ Aviakassa", callback_data="cms_sec_avia"),
        ],
        [
            InlineKeyboardButton(text="📞 Aloqa",  callback_data="cms_sec_contact"),
            InlineKeyboardButton(text="📍 Manzil", callback_data="cms_sec_address"),
        ],
        [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")],
    ])

def kb_cms_section(section):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 UZ matnni o'zgartir", callback_data=f"cms_text_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 RU matnni o'zgartir", callback_data=f"cms_text_{section}_ru"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 UZ tugma qo'sh",  callback_data=f"cms_btnadd_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 RU tugma qo'sh",  callback_data=f"cms_btnadd_{section}_ru"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 UZ tugma o'chir", callback_data=f"cms_btndel_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 RU tugma o'chir", callback_data=f"cms_btndel_{section}_ru"),
        ],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="cms_main")],
    ])

@dp.callback_query(F.data == "cms_main")
async def cms_main(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text(
        "✏️ <b>Kontent boshqaruvi</b>\n\nQaysi bo'limni tahrirlash?",
        reply_markup=kb_cms_main(), parse_mode="HTML"
    )

SECTION_NAMES = {"visa": "🛂 Viza", "avia": "✈️ Aviakassa", "contact": "📞 Aloqa", "address": "📍 Manzil"}

@dp.callback_query(F.data.startswith("cms_sec_"))
async def cms_section(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    section = cb.data.replace("cms_sec_", "")
    name = SECTION_NAMES.get(section, section)
    content = load_content()

    uz_text = content.get(section, {}).get("uz", {}).get("text", "")[:100]
    ru_text = content.get(section, {}).get("ru", {}).get("text", "")[:100]
    uz_btns = content.get(section, {}).get("uz", {}).get("buttons", [])
    ru_btns = content.get(section, {}).get("ru", {}).get("buttons", [])

    info = (
        f"✏️ <b>{name} boshqaruvi</b>\n\n"
        f"🇺🇿 Matn: <i>{uz_text}...</i>\n"
        f"🇺🇿 Tugmalar: {len(uz_btns)} ta\n\n"
        f"🇷🇺 Matn: <i>{ru_text}...</i>\n"
        f"🇷🇺 Tugmalar: {len(ru_btns)} ta"
    )
    await cb.message.edit_text(info, reply_markup=kb_cms_section(section), parse_mode="HTML")

# ─── MATN O'ZGARTIRISH ───────────────────────────────────────

@dp.callback_query(F.data.startswith("cms_text_"))
async def cms_text_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")   # cms_text_visa_uz
    section = parts[2]
    lang    = parts[3]
    content = load_content()
    cur     = content.get(section, {}).get(lang, {}).get("text", "")
    await state.update_data(cms_section=section, cms_lang=lang)
    await cb.message.answer(
        f"✏️ Yangi matnni yozing:\n\n"
        f"<b>HTML teglar ishlatishingiz mumkin:</b>\n"
        f"&lt;b&gt;qalin&lt;/b&gt;, &lt;i&gt;kursiv&lt;/i&gt;\n\n"
        f"<b>Hozirgi matn:</b>\n{cur}",
        parse_mode="HTML"
    )
    await state.set_state(S.cms_text)

@dp.message(S.cms_text)
async def cms_text_save(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    data    = await state.get_data()
    section = data["cms_section"]
    lang    = data["cms_lang"]
    content = load_content()
    content[section][lang]["text"] = msg.text
    save_content(content)
    await msg.answer(
        "✅ <b>Matn saqlandi!</b>\n\nFoydalanuvchilar darhol yangi matnni ko'radi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Yana tahrirlash", callback_data=f"cms_sec_{section}")],
            [InlineKeyboardButton(text="⬅️ Admin panel",     callback_data="adm_main")],
        ]),
        parse_mode="HTML"
    )
    await state.clear()

# ─── TUGMA QO'SHISH ──────────────────────────────────────────

@dp.callback_query(F.data.startswith("cms_btnadd_"))
async def cms_btn_add_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")   # cms_btnadd_visa_uz
    section = parts[2]
    lang    = parts[3]
    await state.update_data(cms_section=section, cms_lang=lang)
    await cb.message.answer(
        "➕ <b>Yangi tugma qo'shish</b>\n\n"
        "Tugma nomini yozing:\n"
        "<i>Masalan: 📞 Bog'lanish</i>",
        parse_mode="HTML"
    )
    await state.set_state(S.cms_btn_text)

@dp.message(S.cms_btn_text)
async def cms_btn_text_save(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    await state.update_data(cms_btn_text=msg.text)
    await msg.answer(
        f"✅ Tugma nomi: <b>{msg.text}</b>\n\n"
        f"Endi tugma URL manzilini yozing:\n"
        f"<i>Masalan: https://t.me/OMAD_TOUR9094</i>",
        parse_mode="HTML"
    )
    await state.set_state(S.cms_btn_url)

@dp.message(S.cms_btn_url)
async def cms_btn_url_save(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    data    = await state.get_data()
    section = data["cms_section"]
    lang    = data["cms_lang"]
    btn_txt = data["cms_btn_text"]
    url     = msg.text.strip()
    content = load_content()
    content[section][lang]["buttons"].append({"text": btn_txt, "url": url})
    save_content(content)
    await msg.answer(
        f"✅ <b>Tugma qo'shildi!</b>\n\n"
        f"Nom: {btn_txt}\n"
        f"URL: {url}\n\n"
        f"Foydalanuvchilar darhol ko'radi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data=f"cms_sec_{section}")],
            [InlineKeyboardButton(text="⬅️ Admin panel",   callback_data="adm_main")],
        ]),
        parse_mode="HTML"
    )
    await state.clear()

# ─── TUGMA O'CHIRISH ─────────────────────────────────────────

@dp.callback_query(F.data.startswith("cms_btndel_"))
async def cms_btn_del_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")   # cms_btndel_visa_uz
    section = parts[2]
    lang    = parts[3]
    content = load_content()
    buttons = content.get(section, {}).get(lang, {}).get("buttons", [])
    if not buttons:
        await cb.answer("Bu bo'limda tugma yo'q!", show_alert=True)
        return
    rows = []
    for i, btn in enumerate(buttons):
        rows.append([InlineKeyboardButton(
            text=f"🗑 {btn['text']}",
            callback_data=f"cms_btnrm_{section}_{lang}_{i}"
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data=f"cms_sec_{section}")])
    await cb.message.edit_text(
        "🗑 <b>Qaysi tugmani o'chirish?</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("cms_btnrm_"))
async def cms_btn_remove(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")   # cms_btnrm_visa_uz_0
    section = parts[2]
    lang    = parts[3]
    idx     = int(parts[4])
    content = load_content()
    buttons = content[section][lang]["buttons"]
    if 0 <= idx < len(buttons):
        removed = buttons.pop(idx)
        save_content(content)
        await cb.message.edit_text(
            f"✅ <b>O'chirildi:</b> {removed['text']}\n\nFoydalanuvchilar darhol ko'radi.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")]
            ]),
            parse_mode="HTML"
        )
    else:
        await cb.answer("Xato!")

# ═══════════════════════════════════════════════════════════════
#  ADMIN — NARXLAR
# ═══════════════════════════════════════════════════════════════
def kb_adm_prices():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Qo'shish",     callback_data="adm_add"),
            InlineKeyboardButton(text="✏️ O'zgartirish", callback_data="adm_edit"),
        ],
        [
            InlineKeyboardButton(text="🗑 O'chirish", callback_data="adm_delete"),
            InlineKeyboardButton(text="📋 Ro'yxat",   callback_data="adm_list"),
        ],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_main")],
    ])

@dp.callback_query(F.data == "adm_prices")
async def adm_prices(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text("💰 <b>Narxlar</b>", reply_markup=kb_adm_prices(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_list")
async def adm_list(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["📋 <b>Narxlar:</b>\n"]
    for i, (d, p) in enumerate(prices.items(), 1):
        lines.append(f"{i}. {d}\n   💰 {p:,} ₽ → mijoz: {p+SBOR:,} ₽\n")
    await cb.message.edit_text("\n".join(lines), reply_markup=kb_adm_prices(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_add")
async def adm_add(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.answer("➕ Yo'nalish nomini yozing:\n<i>Масalan: Санкт-Петербург → Навои</i>", parse_mode="HTML")
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
            reply_markup=kb_adm_prices(), parse_mode="HTML"
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
        idx  = int(msg.text.strip()) - 1
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
            reply_markup=kb_adm_prices(), parse_mode="HTML"
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
        await msg.answer(f"✅ O'chirildi: {d}", reply_markup=kb_adm_prices())
        await state.clear()
    except ValueError:
        await msg.answer("❌ Raqam kiriting!")

# ═══════════════════════════════════════════════════════════════
#  ADMIN — STATISTIKA
# ═══════════════════════════════════════════════════════════════
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
        "<b>So'nggi 20:</b>"
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

# ═══════════════════════════════════════════════════════════════
#  ADMIN — REKLAMA
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.answer(
        "📢 <b>Reklama yuborish</b>\n\nXabarni yozing (matn, rasm, video yoki fayl):",
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

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
