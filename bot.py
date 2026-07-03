cat > /home/claude/bot_v4.py << 'ENDOFFILE'
import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

BOT_TOKEN  = "8949050831:AAHqp6G4hmoiAfYvf095_KN3GjTvIdFtWwY"
ADMIN_ID   = 7359558983
SBOR       = 500
GROUP_LINK = "https://t.me/+OW_pzYSHjIA5NmQy"
GROUP_ID   = -1001490963768  # int, minus bilan

PRICES_F   = "prices.json"
USERS_F    = "users.json"
CONTENT_F  = "content.json"

# ═══════════════════════════════════════════════════════════════
#  DEFAULT KONTENT
# ═══════════════════════════════════════════════════════════════
DEFAULT_CONTENT = {
    "visa": {
        "uz": {
            "photo": "",
            "text": (
                "🛂 <b>Viza bo'limi</b>\n\n"
                "Biz O'zbekiston vizasi bo'yicha to'liq yordam ko'rsatamiz:\n\n"
                "📋 Viza javobi — barcode orqali tekshiring\n"
                "🏛 Konsulstvo guruhi — rasmiy ma'lumotlar\n"
                "📝 Anketa to'ldirish — mutaxassislar yordami\n\n"
                "🇹🇲 Turkmaniston fuqarolari uchun O'zbekiston viza anketasi\n"
                "To'liq yordam ko'rsatamiz.\n\n"
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
            "photo": "",
            "text": (
                "🛂 <b>Визовый отдел</b>\n\n"
                "Мы оказываем полную помощь по визам в Узбекистан:\n\n"
                "📋 Ответ по визе — проверка через штрихкод\n"
                "🏛 Группа консульства — официальная информация\n"
                "📝 Заполнение анкеты — помощь специалистов\n\n"
                "🇹🇲 Для граждан Туркменистана — анкета на визу в Узбекистан\n"
                "Оказываем полную помощь.\n\n"
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
            "photo": "",
            "text": (
                "✈️ <b>Aviakassa — ОМАД ТУР</b>\n\n"
                "Санкт-Петербург dan O'zbekistonga\n"
                "eng arzon aviabiletlar!\n\n"
                "🛫 Barcha yo'nalishlar\n"
                "💼 Bagaj bilan va bagesiz\n"
                "✅ Rasmiy aviakassa\n\n"
                "🕐 Ish vaqti:\n"
                "Dushanba — Shanba: 09:00 — 19:00\n"
                "Yakshanba: Dam olish kuni\n\n"
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
            "photo": "",
            "text": (
                "✈️ <b>Авиакасса — ОМАД ТУР</b>\n\n"
                "Авиабилеты из Санкт-Петербурга\n"
                "в Узбекистан по низким ценам!\n\n"
                "🛫 Все направления\n"
                "💼 С багажом и без\n"
                "✅ Официальная авиакасса\n\n"
                "🕐 Режим работы:\n"
                "Понедельник — Суббота: 09:00 — 19:00\n"
                "Воскресенье: Выходной\n\n"
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
            "photo": "",
            "text": (
                "📞 <b>Tezkor aloqa</b>\n\n"
                "Istalgan vaqt qo'ng'iroq qiling!\n\n"
                "📱 +7 981 193 90 94\n"
                "📱 +7 937 949 90 94\n"
                "📱 +7 921 402 74 89\n\n"
                "🕐 Ish vaqti:\n"
                "Dushanba — Shanba: 09:00 — 19:00\n"
                "Yakshanba: Dam olish kuni"
            ),
            "buttons": []
        },
        "ru": {
            "photo": "",
            "text": (
                "📞 <b>Быстрая связь</b>\n\n"
                "Звоните в любое время!\n\n"
                "📱 +7 981 193 90 94\n"
                "📱 +7 937 949 90 94\n"
                "📱 +7 921 402 74 89\n\n"
                "🕐 Режим работы:\n"
                "Понедельник — Суббота: 09:00 — 19:00\n"
                "Воскресенье: Выходной"
            ),
            "buttons": []
        }
    },
    "address": {
        "uz": {
            "photo": "",
            "text": (
                "📍 <b>Bizning manzillar</b>\n\n"
                "🏢 <b>ОМАД ТУР</b>\n\n"
                "📌 <b>1-ofis (asosiy):</b>\n"
                "Metro: Технологический институт\n"
                "ул. 4-я Красноармейская, дом 3\n"
                "Домофон: 22Б\n\n"
                "📌 <b>2-ofis:</b>\n"
                "просп. Большевиков, 24, корп. 1\n\n"
                "🕐 Ish vaqti:\n"
                "Dushanba — Shanba: 09:00 — 19:00\n"
                "Yakshanba: Dam olish kuni"
            ),
            "buttons": [
                {"text": "🗺 1-ofis — 4-я Красноармейская", "url": "https://yandex.ru/maps/-/CLaRUCPW"},
                {"text": "🗺 2-ofis — Большевиков",          "url": "https://yandex.ru/maps/org/omad_tour/50809406614"},
            ]
        },
        "ru": {
            "photo": "",
            "text": (
                "📍 <b>Наши адреса</b>\n\n"
                "🏢 <b>ОМАД ТУР</b>\n\n"
                "📌 <b>Офис 1 (основной):</b>\n"
                "Метро: Технологический институт\n"
                "ул. 4-я Красноармейская, дом 3\n"
                "Домофон: 22Б\n\n"
                "📌 <b>Офис 2:</b>\n"
                "просп. Большевиков, 24, корп. 1\n\n"
                "🕐 Режим работы:\n"
                "Понедельник — Суббота: 09:00 — 19:00\n"
                "Воскресенье: Выходной"
            ),
            "buttons": [
                {"text": "🗺 Офис 1 — 4-я Красноармейская", "url": "https://yandex.ru/maps/-/CLaRUCPW"},
                {"text": "🗺 Офис 2 — Большевиков",          "url": "https://yandex.ru/maps/org/omad_tour/50809406614"},
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
#  FAYLLAR
# ═══════════════════════════════════════════════════════════════
def load_content():
    if os.path.exists(CONTENT_F):
        with open(CONTENT_F, "r", encoding="utf-8") as f:
            return json.load(f)
    data = json.loads(json.dumps(DEFAULT_CONTENT))
    save_content(data)
    return data

def save_content(data):
    with open(CONTENT_F, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_prices():
    if os.path.exists(PRICES_F):
        with open(PRICES_F, "r", encoding="utf-8") as f:
            return json.load(f)
    p = dict(DEFAULT_PRICES)
    save_prices(p)
    return p

def save_prices(data):
    with open(PRICES_F, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists(USERS_F):
        with open(USERS_F, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def write_users(users):
    with open(USERS_F, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════════════════════════════
#  BOT
# ═══════════════════════════════════════════════════════════════
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

class S(StatesGroup):
    phone         = State()
    question      = State()
    reply         = State()
    broadcast     = State()
    cms_text      = State()
    cms_photo     = State()
    cms_btn_text  = State()
    cms_btn_url   = State()
    add_dir       = State()
    add_price     = State()
    edit_select   = State()
    edit_price    = State()
    delete_select = State()

# ═══════════════════════════════════════════════════════════════
#  GURUH TEKSHIRISH — TO'G'RI USUL
# ═══════════════════════════════════════════════════════════════
async def is_member(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        status = member.status
        return status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        logging.warning(f"Guruh tekshirish xatosi: {e}")
        # Agar xato bo'lsa — o'tkazib yuboramiz
        return True

# ═══════════════════════════════════════════════════════════════
#  KLAVIATURALAR
# ═══════════════════════════════════════════════════════════════
def kb_subscribe():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📢 Guruhga qo'shilish / Вступить в группу",
            url=GROUP_LINK
        )],
        [InlineKeyboardButton(
            text="✅ A'zo bo'ldim / Я вступил",
            callback_data="check_sub"
        )],
    ])

def kb_main(lang):
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🛂 Viza bo'limi" if uz else "🛂 Визовый отдел",
                callback_data=f"sec_visa_{lang}"
            ),
            InlineKeyboardButton(
                text="✈️ Aviakassa" if uz else "✈️ Авиакасса",
                callback_data=f"sec_avia_{lang}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📞 Tezkor aloqa" if uz else "📞 Быстрая связь",
                callback_data=f"sec_contact_{lang}"
            ),
            InlineKeyboardButton(
                text="📍 Manzil" if uz else "📍 Адрес",
                callback_data=f"sec_address_{lang}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="❓ Savol yuborish" if uz else "❓ Задать вопрос",
                callback_data=f"question_{lang}"
            ),
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

def kb_section(section, lang):
    content = load_content()
    buttons = content.get(section, {}).get(lang, {}).get("buttons", [])
    rows = []
    pair = []
    for btn in buttons:
        pair.append(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([InlineKeyboardButton(
        text="⬅️ Ortga" if lang == "uz" else "⬅️ Назад",
        callback_data=f"home_{lang}"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_admin():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Kontent boshqaruvi", callback_data="cms_main")],
        [InlineKeyboardButton(text="💰 Narxlar",            callback_data="adm_prices")],
        [InlineKeyboardButton(text="📊 Statistika",         callback_data="adm_stats")],
        [InlineKeyboardButton(text="📢 Reklama yuborish",   callback_data="adm_broadcast")],
    ])

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
            InlineKeyboardButton(text="🇺🇿 UZ matn",      callback_data=f"cms_text_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 RU matn",      callback_data=f"cms_text_{section}_ru"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 UZ rasm",      callback_data=f"cms_photo_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 RU rasm",      callback_data=f"cms_photo_{section}_ru"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 Tugma qo'sh",  callback_data=f"cms_btnadd_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 Tugma qo'sh",  callback_data=f"cms_btnadd_{section}_ru"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 Tugma o'chir", callback_data=f"cms_btndel_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 Tugma o'chir", callback_data=f"cms_btndel_{section}_ru"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 Ko'rish", callback_data=f"preview_{section}_uz"),
            InlineKeyboardButton(text="🇷🇺 Ko'rish", callback_data=f"preview_{section}_ru"),
        ],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="cms_main")],
    ])

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

# ═══════════════════════════════════════════════════════════════
#  SECTION YUBORISH
# ═══════════════════════════════════════════════════════════════
async def send_section(target, section, lang):
    content = load_content()
    sec     = content.get(section, {}).get(lang, {})
    text    = sec.get("text", "...")
    photo   = sec.get("photo", "")
    kb      = kb_section(section, lang)

    if photo:
        try:
            if hasattr(target, "message"):
                await target.message.delete()
                await target.message.answer_photo(photo=photo, caption=text, reply_markup=kb, parse_mode="HTML")
            else:
                await target.answer_photo(photo=photo, caption=text, reply_markup=kb, parse_mode="HTML")
            return
        except Exception as e:
            logging.warning(f"Rasm yuborishda xato: {e}")

    if hasattr(target, "message"):
        try:
            await target.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except:
            await target.message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=kb, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  START
# ═══════════════════════════════════════════════════════════════
async def show_main_menu(msg: Message, user):
    users = load_users()
    if str(user.id) not in users:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(
                text="📱 Raqamni ulashish / Поделиться номером",
                request_contact=True
            )]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await msg.answer(
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "Davom etish uchun telefon raqamingizni ulashing:\n\n"
            "👋 <b>Добро пожаловать!</b>\n\n"
            "Для продолжения поделитесь номером телефона:",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return False
    await msg.answer(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")
    return True

@dp.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    user = msg.from_user

    subscribed = await is_member(user.id)
    if not subscribed:
        await msg.answer(
            "📢 <b>Guruhimizga a'zo bo'ling!</b>\n\n"
            "Yangi biletlar narxi va aksiyalar bilan tanishib chiqing.\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "📢 <b>Вступите в нашу группу!</b>\n\n"
            "Узнайте актуальные цены на билеты и специальные акции.",
            reply_markup=kb_subscribe(),
            parse_mode="HTML"
        )
        return

    users = load_users()
    if str(user.id) not in users:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(
                text="📱 Raqamni ulashish / Поделиться номером",
                request_contact=True
            )]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await msg.answer(
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "Davom etish uchun telefon raqamingizni ulashing:\n\n"
            "👋 <b>Добро пожаловать!</b>\n\n"
            "Для продолжения поделитесь номером телефона:",
            reply_markup=kb,
            parse_mode="HTML"
        )
        await state.set_state(S.phone)
        return

    await msg.answer(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  OBUNA TEKSHIRISH TUGMASI
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "check_sub")
async def check_sub(cb: CallbackQuery, state: FSMContext):
    user = cb.from_user
    subscribed = await is_member(user.id)

    if not subscribed:
        await cb.answer(
            "❌ Siz hali guruhga a'zo emassiz!\n❌ Вы ещё не вступили в группу!",
            show_alert=True
        )
        return

    users = load_users()
    if str(user.id) not in users:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(
                text="📱 Raqamni ulashish / Поделиться номером",
                request_contact=True
            )]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await cb.message.answer(
            "✅ <b>Ajoyib! Guruhga a'zo bo'ldingiz!</b>\n\n"
            "Davom etish uchun telefon raqamingizni ulashing:\n\n"
            "✅ <b>Отлично! Вы вступили в группу!</b>\n\n"
            "Для продолжения поделитесь номером телефона:",
            reply_markup=kb,
            parse_mode="HTML"
        )
        await state.set_state(S.phone)
    else:
        try:
            await cb.message.edit_text(
                txt_home("uz"),
                reply_markup=kb_main("uz"),
                parse_mode="HTML"
            )
        except:
            await cb.message.answer(
                txt_home("uz"),
                reply_markup=kb_main("uz"),
                parse_mode="HTML"
            )

# ═══════════════════════════════════════════════════════════════
#  TELEFON RAQAM
# ═══════════════════════════════════════════════════════════════
@dp.message(S.phone)
async def get_phone(msg: Message, state: FSMContext):
    user = msg.from_user
    if not msg.contact:
        await msg.answer("📱 Iltimos tugmani bosing! / Пожалуйста, нажмите кнопку!")
        return

    phone = msg.contact.phone_number
    users = load_users()
    is_new = str(user.id) not in users
    users[str(user.id)] = {
        "username":  user.username or "",
        "full_name": user.full_name,
        "phone":     phone,
        "visits":    1
    }
    write_users(users)

    if is_new:
        uname = f"@{user.username}" if user.username else "—"
        await bot.send_message(
            ADMIN_ID,
            f"🆕 <b>Yangi foydalanuvchi!</b>\n\n"
            f"👤 Ism: <b>{user.full_name}</b>\n"
            f"📱 Username: {uname}\n"
            f"📞 Tel: <b>{phone}</b>\n"
            f"🆔 ID: <code>{user.id}</code>",
            parse_mode="HTML"
        )

    await msg.answer("✅ Rahmat!", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.3)
    await msg.answer(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")
    await state.clear()

# ═══════════════════════════════════════════════════════════════
#  ADMIN
# ═══════════════════════════════════════════════════════════════
@dp.message(Command("admin"))
async def cmd_admin(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("🔧 <b>Admin panel</b>", reply_markup=kb_admin(), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  TIL / HOME
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "lang_uz")
async def lang_uz(cb: CallbackQuery):
    try:
        await cb.message.edit_text(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")
    except:
        await cb.message.answer(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "lang_ru")
async def lang_ru(cb: CallbackQuery):
    try:
        await cb.message.edit_text(txt_home("ru"), reply_markup=kb_main("ru"), parse_mode="HTML")
    except:
        await cb.message.answer(txt_home("ru"), reply_markup=kb_main("ru"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("home_"))
async def go_home(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    try:
        await cb.message.edit_text(txt_home(lang), reply_markup=kb_main(lang), parse_mode="HTML")
    except:
        await cb.message.answer(txt_home(lang), reply_markup=kb_main(lang), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  BO'LIMLAR
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("sec_"))
async def show_section(cb: CallbackQuery):
    parts   = cb.data.split("_")
    section = parts[1]
    lang    = parts[2]
    await send_section(cb, section, lang)

# ═══════════════════════════════════════════════════════════════
#  SAVOL
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("question_"))
async def question_section(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await state.update_data(lang=lang)
    uz = lang == "uz"
    text = (
        "✉️ <b>Savol yuborish</b>\n\n"
        "Savolingizni yozing yoki\n"
        "rasm / video / fayl / ovoz yuboring.\n\n"
        "Tez orada javob beramiz! 🙏"
        if uz else
        "✉️ <b>Задать вопрос</b>\n\n"
        "Напишите вопрос или отправьте\n"
        "фото / видео / файл / голос.\n\n"
        "Ответим как можно скорее! 🙏"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"home_{lang}"
        )]
    ])
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(S.question)

@dp.message(S.question)
async def receive_question(msg: Message, state: FSMContext):
    data  = await state.get_data()
    lang  = data.get("lang", "uz")
    user  = msg.from_user
    uname = f"@{user.username}" if user.username else "—"
    users = load_users()
    phone = users.get(str(user.id), {}).get("phone", "—")

    header = (
        f"📨 <b>Yangi savol!</b>\n\n"
        f"👤 {user.full_name}\n"
        f"📱 {uname}\n"
        f"📞 {phone}\n"
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

# ═══════════════════════════════════════════════════════════════
#  ADMIN JAVOB
# ═══════════════════════════════════════════════════════════════
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
        await msg.answer("✅ Javob yuborildi!", reply_markup=kb_admin())
    except Exception as e:
        await msg.answer(f"❌ Xato: {e}")
    await state.clear()

# ═══════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "adm_main")
async def adm_main(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    try:
        await cb.message.edit_text("🔧 <b>Admin panel</b>", reply_markup=kb_admin(), parse_mode="HTML")
    except:
        await cb.message.answer("🔧 <b>Admin panel</b>", reply_markup=kb_admin(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_stats")
async def adm_stats(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    users  = load_users()
    total  = len(users)
    visits = sum(u.get("visits", 1) for u in users.values())
    lines  = [
        f"📊 <b>Statistika</b>\n",
        f"👥 Foydalanuvchilar: <b>{total}</b>",
        f"🔢 Jami tashriflar: <b>{visits}</b>\n",
        "<b>So'nggi 20:</b>"
    ]
    for i, (uid, u) in enumerate(list(users.items())[-20:], 1):
        uname = f"@{u['username']}" if u.get("username") else "—"
        phone = u.get("phone", "—")
        lines.append(f"{i}. {u['full_name']} | {uname} | {phone}")
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
    users = load_users()
    await cb.message.answer(
        f"📢 <b>Reklama yuborish</b>\n\n"
        f"👥 Jami: {len(users)} foydalanuvchi\n\n"
        f"Xabarni yozing (matn, rasm, video yoki fayl):",
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
        reply_markup=kb_admin(), parse_mode="HTML"
    )
    await state.clear()

# ═══════════════════════════════════════════════════════════════
#  CMS
# ═══════════════════════════════════════════════════════════════
SECTION_NAMES = {
    "visa": "🛂 Viza", "avia": "✈️ Aviakassa",
    "contact": "📞 Aloqa", "address": "📍 Manzil"
}

@dp.callback_query(F.data == "cms_main")
async def cms_main(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text(
        "✏️ <b>Kontent boshqaruvi</b>\n\nQaysi bo'limni tahrirlash?",
        reply_markup=kb_cms_main(), parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("cms_sec_"))
async def cms_sec(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    section = cb.data.replace("cms_sec_", "")
    name    = SECTION_NAMES.get(section, section)
    content = load_content()
    uz_btns  = len(content.get(section, {}).get("uz", {}).get("buttons", []))
    ru_btns  = len(content.get(section, {}).get("ru", {}).get("buttons", []))
    uz_photo = "✅" if content.get(section, {}).get("uz", {}).get("photo") else "❌"
    ru_photo = "✅" if content.get(section, {}).get("ru", {}).get("photo") else "❌"
    info = (
        f"✏️ <b>{name}</b>\n\n"
        f"🇺🇿 Rasm: {uz_photo} | Tugmalar: {uz_btns} ta\n"
        f"🇷🇺 Rasm: {ru_photo} | Tugmalar: {ru_btns} ta\n\n"
        f"Nimani o'zgartirish?"
    )
    try:
        await cb.message.edit_text(info, reply_markup=kb_cms_section(section), parse_mode="HTML")
    except:
        await cb.message.answer(info, reply_markup=kb_cms_section(section), parse_mode="HTML")

@dp.callback_query(F.data.startswith("preview_"))
async def preview_section(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")
    section = parts[1]
    lang    = parts[2]
    await cb.message.answer("👁 <b>Ko'rinish:</b>", parse_mode="HTML")
    await send_section(cb.message, section, lang)

@dp.callback_query(F.data.startswith("cms_text_"))
async def cms_text_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")
    section = parts[2]
    lang    = parts[3]
    content = load_content()
    cur     = content.get(section, {}).get(lang, {}).get("text", "")
    await state.update_data(cms_section=section, cms_lang=lang)
    await cb.message.answer(
        f"✏️ <b>Yangi matnni yozing</b>\n\n"
        f"HTML: &lt;b&gt;qalin&lt;/b&gt;, &lt;i&gt;kursiv&lt;/i&gt;\n\n"
        f"<b>Hozirgi matn:</b>\n{cur[:300]}",
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
        "✅ <b>Matn saqlandi!</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👁 Ko'rish",     callback_data=f"preview_{section}_{lang}")],
            [InlineKeyboardButton(text="✏️ Bo'lim",      callback_data=f"cms_sec_{section}")],
            [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")],
        ]),
        parse_mode="HTML"
    )
    await state.clear()

@dp.callback_query(F.data.startswith("cms_photo_"))
async def cms_photo_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")
    section = parts[2]
    lang    = parts[3]
    await state.update_data(cms_section=section, cms_lang=lang)
    await cb.message.answer(
        "🖼 Rasmni yuboring yoki o'chirish uchun <code>o'chir</code> yozing",
        parse_mode="HTML"
    )
    await state.set_state(S.cms_photo)

@dp.message(S.cms_photo)
async def cms_photo_save(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    data    = await state.get_data()
    section = data["cms_section"]
    lang    = data["cms_lang"]
    content = load_content()
    if msg.text and msg.text.strip().lower() in ["o'chir", "ochir", "удалить"]:
        content[section][lang]["photo"] = ""
        save_content(content)
        await msg.answer("✅ Rasm o'chirildi!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Bo'lim", callback_data=f"cms_sec_{section}")]
        ]))
    elif msg.photo:
        content[section][lang]["photo"] = msg.photo[-1].file_id
        save_content(content)
        await msg.answer(
            "✅ <b>Rasm saqlandi!</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👁 Ko'rish",     callback_data=f"preview_{section}_{lang}")],
                [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")],
            ]),
            parse_mode="HTML"
        )
    else:
        await msg.answer("❌ Rasm yuboring!")
        return
    await state.clear()

@dp.callback_query(F.data.startswith("cms_btnadd_"))
async def cms_btnadd_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")
    section = parts[2]
    lang    = parts[3]
    await state.update_data(cms_section=section, cms_lang=lang)
    await cb.message.answer(
        "➕ Tugma nomini yozing:\n<i>Masalan: 📞 Bog'lanish</i>",
        parse_mode="HTML"
    )
    await state.set_state(S.cms_btn_text)

@dp.message(S.cms_btn_text)
async def cms_btn_text(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    await state.update_data(cms_btn_text=msg.text)
    await msg.answer(
        f"✅ Nom: <b>{msg.text}</b>\n\nURL manzilini yozing:",
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
        f"✅ Tugma qo'shildi!\n📌 {btn_txt}\n🔗 {url}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yana",        callback_data=f"cms_btnadd_{section}_{lang}")],
            [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")],
        ]),
        parse_mode="HTML"
    )
    await state.clear()

@dp.callback_query(F.data.startswith("cms_btndel_"))
async def cms_btndel_start(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")
    section = parts[2]
    lang    = parts[3]
    content = load_content()
    buttons = content.get(section, {}).get(lang, {}).get("buttons", [])
    if not buttons:
        await cb.answer("Tugma yo'q!", show_alert=True)
        return
    rows = []
    for i, btn in enumerate(buttons):
        rows.append([InlineKeyboardButton(
            text=f"🗑 {btn['text']}",
            callback_data=f"cms_btnrm_{section}_{lang}_{i}"
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data=f"cms_sec_{section}")])
    await cb.message.edit_text(
        "🗑 Qaysi tugmani o'chirish?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )

@dp.callback_query(F.data.startswith("cms_btnrm_"))
async def cms_btn_remove(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    parts   = cb.data.split("_")
    section = parts[2]
    lang    = parts[3]
    idx     = int(parts[4])
    content = load_content()
    buttons = content[section][lang]["buttons"]
    if 0 <= idx < len(buttons):
        removed = buttons.pop(idx)
        save_content(content)
        await cb.message.edit_text(
            f"✅ O'chirildi: <b>{removed['text']}</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")]
            ]),
            parse_mode="HTML"
        )

# ═══════════════════════════════════════════════════════════════
#  NARXLAR
# ═══════════════════════════════════════════════════════════════
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
        lines.append(f"{i}. {d}\n   💰 {p:,} ₽ → {p+SBOR:,} ₽\n")
    await cb.message.edit_text("\n".join(lines), reply_markup=kb_adm_prices(), parse_mode="HTML")

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
            f"✅ {d}\n💰 {price:,} ₽ → {price+SBOR:,} ₽",
            reply_markup=kb_adm_prices(), parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await msg.answer("❌ Faqat raqam!")

@dp.callback_query(F.data == "adm_edit")
async def adm_edit(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["✏️ Raqamini yozing:\n"]
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
            await msg.answer("❌ Noto'g'ri!")
            return
        await state.update_data(direction=dirs[idx])
        await msg.answer(f"✏️ <b>{dirs[idx]}</b>\n\nYangi narx:", parse_mode="HTML")
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
    lines  = ["🗑 Raqamini yozing:\n"]
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
            await msg.answer("❌ Noto'g'ri!")
            return
        d = dirs[idx]
        del p[d]
        save_prices(p)
        await msg.answer(f"✅ O'chirildi: {d}", reply_markup=kb_adm_prices())
        await state.clear()
    except ValueError:
        await msg.answer("❌ Raqam kiriting!")

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
ENDOFFILE
echo "DONE — $(wc -l < /home/claude/bot_v4.py) qator"
