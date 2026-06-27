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

# ═══════════════════════════════════════════════════════════════
#  SOZLAMALAR
# ═══════════════════════════════════════════════════════════════
BOT_TOKEN  = "8949050831:AAHqp6G4hmoiAfYvf095_KN3GjTvIdFtWwY"
ADMIN_ID   = 7359558983
SBOR       = 500          # yashirin xizmat ulushi
PRICES_F   = "prices.json"
USERS_F    = "users.json"

# ═══════════════════════════════════════════════════════════════
#  HELPERS — fayl o'qish / yozish
# ═══════════════════════════════════════════════════════════════
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

def load_prices() -> dict:
    if os.path.exists(PRICES_F):
        with open(PRICES_F, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict(DEFAULT_PRICES)

def save_prices(data: dict):
    with open(PRICES_F, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users() -> dict:
    if os.path.exists(USERS_F):
        with open(USERS_F, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def register_user(uid: int, username: str | None, full_name: str):
    users = load_users()
    key = str(uid)
    if key not in users:
        users[key] = {"username": username or "", "full_name": full_name, "visits": 1}
    else:
        users[key]["visits"] += 1
    with open(USERS_F, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════════════════════════════
#  BOT VA DISPATCHER
# ═══════════════════════════════════════════════════════════════
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

# ═══════════════════════════════════════════════════════════════
#  HOLATLAR (FSM)
# ═══════════════════════════════════════════════════════════════
class S(StatesGroup):
    question         = State()   # foydalanuvchi savol yozadi
    reply            = State()   # admin javob yozadi
    broadcast        = State()   # admin reklama yozadi
    add_dir          = State()   # admin yo'nalish nomi
    add_price        = State()   # admin narx
    edit_select      = State()   # admin tahrir — raqam tanlash
    edit_price       = State()   # admin tahrir — yangi narx
    delete_select    = State()   # admin o'chirish — raqam

# ═══════════════════════════════════════════════════════════════
#  INLINE KLAVIATURALAR
# ═══════════════════════════════════════════════════════════════

def kb_main(lang: str) -> InlineKeyboardMarkup:
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🛂 Viza bo'limi"  if uz else "🛂 Визовый отдел",
                callback_data="sec_visa"
            ),
            InlineKeyboardButton(
                text="✈️ Aviakassa" if uz else "✈️ Авиакасса",
                callback_data="sec_avia"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📞 Tezkor aloqa" if uz else "📞 Быстрая связь",
                callback_data="sec_contact"
            ),
            InlineKeyboardButton(
                text="📍 Manzil" if uz else "📍 Адрес",
                callback_data="sec_address"
            ),
        ],
        [
            InlineKeyboardButton(
                text="❓ Savol yuborish" if uz else "❓ Задать вопрос",
                callback_data="sec_question"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🇷🇺 Русский" if uz else "🇺🇿 O'zbek",
                callback_data="set_lang_ru" if uz else "set_lang_uz"
            ),
        ],
    ])

def kb_back(lang: str, to: str = "home") -> InlineKeyboardMarkup:
    text = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"go_{to}_{lang}")]
    ])

def kb_visa(lang: str) -> InlineKeyboardMarkup:
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 Viza javobi" if uz else "📋 Ответ по визе",
            callback_data=f"visa_answer_{lang}"
        )],
        [InlineKeyboardButton(
            text="🏛 O'zb Konsulstvo guruhi" if uz else "🏛 Группа Консульства Узб",
            callback_data=f"visa_consul_{lang}"
        )],
        [InlineKeyboardButton(
            text="📝 Anketa to'ldirish" if uz else "📝 Заполнить анкету",
            callback_data=f"visa_anketa_{lang}"
        )],
        [InlineKeyboardButton(
            text="🇹🇲 Turkman fuqarolari uchun O'zb viza" if uz else "🇹🇲 Виза Узб для граждан Туркменистана",
            callback_data=f"visa_turkmen_{lang}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_home_{lang}"
        )],
    ])

def kb_avia(lang: str) -> InlineKeyboardMarkup:
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Telegram", url="https://t.me/OMAD_TOUR9094"),
            InlineKeyboardButton(text="💚 WhatsApp",  url="https://wa.me/79811939094"),
        ],
        [
            InlineKeyboardButton(text="📱 IMO",  url="https://t.me/OMAD_TOUR9094"),
            InlineKeyboardButton(text="🔵 Max",  url="https://max.ru/u/f9LHodD0cOLLpEmAWC_I3iUUWcn5IO6DFYg0IVz4jEXfm6BJP6OL-L7V0jk"),
        ],
        [InlineKeyboardButton(
            text="💰 Narxlarni ko'rish" if uz else "💰 Посмотреть цены",
            callback_data=f"sec_prices_{lang}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_home_{lang}"
        )],
    ])

def kb_contact(lang: str) -> InlineKeyboardMarkup:
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 +7 981 193 90 94", url="tel:+79811939094")],
        [InlineKeyboardButton(text="📞 +7 921 402 74 89", url="tel:+79214027489")],
        [InlineKeyboardButton(text="📞 +7 937 949 90 94", url="tel:+79379499094")],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_home_{lang}"
        )],
    ])

def kb_address(lang: str) -> InlineKeyboardMarkup:
    uz = lang == "uz"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🗺 1-ofis xaritada" if uz else "🗺 Офис 1 на карте",
            url="https://yandex.ru/maps/-/CLaRUCPW"
        )],
        [InlineKeyboardButton(
            text="🗺 2-ofis xaritada" if uz else "🗺 Офис 2 на карте",
            url="https://yandex.ru/maps/org/omad_tour/50809406614"
        )],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_home_{lang}"
        )],
    ])

def kb_prices(lang: str) -> InlineKeyboardMarkup:
    prices = load_prices()
    rows = []
    for i, direction in enumerate(prices):
        rows.append([InlineKeyboardButton(
            text=f"✈️ {direction}",
            callback_data=f"price_dir_{lang}_{i}"
        )])
    rows.append([InlineKeyboardButton(
        text="⬅️ Ortga" if lang == "uz" else "⬅️ Назад",
        callback_data=f"sec_avia"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_admin_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika",       callback_data="adm_stats")],
        [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="💰 Narxlar",          callback_data="adm_prices")],
    ])

def kb_admin_prices() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Qo'shish",      callback_data="adm_add"),
            InlineKeyboardButton(text="✏️ O'zgartirish",  callback_data="adm_edit"),
        ],
        [
            InlineKeyboardButton(text="🗑 O'chirish",     callback_data="adm_delete"),
            InlineKeyboardButton(text="📋 Ro'yxat",       callback_data="adm_list"),
        ],
        [InlineKeyboardButton(text="⬅️ Ortga",            callback_data="adm_back")],
    ])

# ═══════════════════════════════════════════════════════════════
#  MATNLAR
# ═══════════════════════════════════════════════════════════════
def txt_home(lang: str) -> str:
    if lang == "uz":
        return (
            "✈️ <b>ОМАД ТУР</b> — Aviakassa\n\n"
            "Xush kelibsiz! Kerakli bo'limni tanlang 👇"
        )
    return (
        "✈️ <b>ОМАД ТУР</b> — Авиакасса\n\n"
        "Добро пожаловать! Выберите нужный раздел 👇"
    )

# ═══════════════════════════════════════════════════════════════
#  /start  /admin
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
#  TIL TANLASH
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "set_lang_uz")
async def set_uz(cb: CallbackQuery):
    await cb.message.edit_text(txt_home("uz"), reply_markup=kb_main("uz"), parse_mode="HTML")

@dp.callback_query(F.data == "set_lang_ru")
async def set_ru(cb: CallbackQuery):
    await cb.message.edit_text(txt_home("ru"), reply_markup=kb_main("ru"), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  ORTGA (universal)
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("go_home_"))
async def go_home(cb: CallbackQuery):
    lang = cb.data.split("_")[2]
    await cb.message.edit_text(txt_home(lang), reply_markup=kb_main(lang), parse_mode="HTML")

@dp.callback_query(F.data.startswith("go_visa_"))
async def go_visa(cb: CallbackQuery):
    lang = cb.data.split("_")[2]
    await cb.message.edit_text(
        "🛂 <b>Viza bo'limi</b>\n\nKerakli xizmatni tanlang 👇" if lang == "uz"
        else "🛂 <b>Визовый отдел</b>\n\nВыберите нужную услугу 👇",
        reply_markup=kb_visa(lang), parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
#  ASOSIY BO'LIMLAR
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "sec_visa")
async def sec_visa(cb: CallbackQuery):
    lang = "uz"
    await cb.message.edit_text(
        "🛂 <b>Viza bo'limi</b>\n\n"
        "O'zbekiston vizasi va konsullik xizmatlari bo'yicha\n"
        "to'liq yordam ko'rsatamiz.\n\n"
        "Kerakli xizmatni tanlang 👇",
        reply_markup=kb_visa(lang), parse_mode="HTML"
    )

@dp.callback_query(F.data == "sec_avia")
async def sec_avia(cb: CallbackQuery):
    # tilni avia kontentidan olish mumkin emas, shuning uchun uzdan boshlaymiz
    await cb.message.edit_text(
        "✈️ <b>Aviakassa — ОМАД ТУР</b>\n\n"
        "Санкт-Петербург dan O'zbekistonga\n"
        "eng arzon aviabiletlar!\n\n"
        "🛫 Barcha yo'nalishlar\n"
        "💼 Bagaj bilan va bagesiz\n"
        "✅ Rasmiy aviakassa\n\n"
        "Biz bilan bog'laning 👇",
        reply_markup=kb_avia("uz"), parse_mode="HTML"
    )

@dp.callback_query(F.data == "sec_contact")
async def sec_contact(cb: CallbackQuery):
    await cb.message.edit_text(
        "📞 <b>Tezkor aloqa</b>\n\n"
        "Istalgan vaqt qo'ng'iroq qiling!\n"
        "Doim yordam berishga tayyormiz 🙏\n\n"
        "👇 Raqamni bosing — qo'ng'iroq ochiladi:",
        reply_markup=kb_contact("uz"), parse_mode="HTML"
    )

@dp.callback_query(F.data == "sec_address")
async def sec_address(cb: CallbackQuery):
    await cb.message.edit_text(
        "📍 <b>Bizning manzillar</b>\n\n"
        "🏢 <b>ОМАД ТУР</b>\n\n"
        "📌 <b>1-ofis:</b>\n"
        "просп. Большевиков, 24, корп. 1\n\n"
        "📌 <b>2-ofis:</b>\n"
        "ул. 4-я Красноармейская, дом 3\n\n"
        "🕐 Ish vaqti: 09:00 — 21:00 (har kuni)\n\n"
        "👇 Xaritada ko'rish uchun bosing:",
        reply_markup=kb_address("uz"), parse_mode="HTML"
    )

@dp.callback_query(F.data == "sec_question")
async def sec_question(cb: CallbackQuery, state: FSMContext):
    await state.update_data(lang="uz", reply_msg_id=cb.message.message_id)
    await cb.message.edit_text(
        "✉️ <b>Savol yuborish</b>\n\n"
        "Savolingizni yozing yoki\n"
        "rasm / video / fayl / ovoz yuboring.\n\n"
        "Tez orada javob beramiz! 🙏",
        reply_markup=kb_back("uz", "home"), parse_mode="HTML"
    )
    await state.set_state(S.question)

# Rus tili versiyalari
@dp.callback_query(F.data.startswith("sec_visa_ru"))
async def sec_visa_ru(cb: CallbackQuery):
    await cb.message.edit_text(
        "🛂 <b>Визовый отдел</b>\n\n"
        "Оказываем полную помощь по визам\n"
        "в Узбекистан и консульским услугам.\n\n"
        "Выберите нужный раздел 👇",
        reply_markup=kb_visa("ru"), parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("sec_prices_"))
async def sec_prices(cb: CallbackQuery):
    lang = cb.data.split("_")[2]
    title = "✈️ <b>Yo'nalishni tanlang:</b>" if lang == "uz" else "✈️ <b>Выберите направление:</b>"
    await cb.message.edit_text(title, reply_markup=kb_prices(lang), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  NARX TAFSILOTI
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("price_dir_"))
async def price_detail(cb: CallbackQuery):
    _, _, lang, idx_s = cb.data.split("_", 3)
    # "price_dir_uz_2" => lang="uz", idx_s="2"
    # lekin split("_",3) => ["price","dir","uz","2"]
    lang = cb.data.split("_")[2]
    idx  = int(cb.data.split("_")[3])
    prices     = load_prices()
    directions = list(prices.keys())
    if idx >= len(directions):
        await cb.answer("❌ Topilmadi")
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
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data=f"sec_prices_uz")],
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
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"sec_prices_ru")],
        ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  VIZA BO'LIMLARI
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("visa_answer_"))
async def visa_answer(cb: CallbackQuery):
    lang = cb.data.split("_")[2]
    uz = lang == "uz"
    text = (
        "📋 <b>Viza javobi</b>\n\n"
        "O'zbekiston vizangiz holati haqida ma'lumot olish uchun "
        "barcode orqali tekshirishingiz mumkin.\n\n"
        "✅ Natija bir necha daqiqada tayyorlanadi\n\n"
        "👇 Quyidagi tugmani bosing:"
        if uz else
        "📋 <b>Ответ по визе</b>\n\n"
        "Для получения информации о статусе вашей визы "
        "в Узбекистан можно проверить через штрихкод.\n\n"
        "✅ Результат готовится в течение нескольких минут\n\n"
        "👇 Нажмите кнопку ниже:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔍 Viza javobini tekshirish" if uz else "🔍 Проверить ответ по визе",
            url="https://t.me/ISHONCHLI_AVIAKASSA9094_BOT/visa"
        )],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_visa_{lang}"
        )],
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("visa_consul_"))
async def visa_consul(cb: CallbackQuery):
    lang = cb.data.split("_")[2]
    uz = lang == "uz"
    text = (
        "🏛 <b>Sankt-Peterburgdagi O'zbekiston Elchixonasi</b>\n\n"
        "Rasmiy konsullik xizmatlari va ma'lumotlar uchun "
        "O'zbekiston Konsulstvo guruhiga qo'shilishingiz mumkin.\n\n"
        "📌 Guruhda topasiz:\n"
        "• Rasmiy e'lonlar va yangiliklar\n"
        "• Viza va hujjatlar bo'yicha ma'lumotlar\n"
        "• Konsullik qabulxonasi ish vaqti\n\n"
        "👇 Bosing:"
        if uz else
        "🏛 <b>Консульство Узбекистана в Санкт-Петербурге</b>\n\n"
        "Для получения официальной консульской информации "
        "вы можете вступить в группу Консульства Узбекистана.\n\n"
        "📌 В группе найдёте:\n"
        "• Официальные объявления и новости\n"
        "• Информацию по визам и документам\n"
        "• Часы работы консульского отдела\n\n"
        "👇 Нажмите:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🏛 Guruhga qo'shilish" if uz else "🏛 Вступить в группу",
            url="https://t.me/+i8I6ByH_CUVhOWQy"
        )],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_visa_{lang}"
        )],
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("visa_anketa_"))
async def visa_anketa(cb: CallbackQuery):
    lang = cb.data.split("_")[2]
    uz = lang == "uz"
    text = (
        "📝 <b>Anketa to'ldirish xizmati</b>\n\n"
        "Viza uchun anketa to'ldirishda yordam kerakmi?\n\n"
        "✅ Mutaxassislarimiz sizga yordam beradi:\n"
        "• Anketani to'g'ri to'ldirish\n"
        "• Hujjatlarni tayyorlash\n"
        "• Ariza topshirish\n\n"
        "👇 Murojaat qiling:"
        if uz else
        "📝 <b>Услуга заполнения анкеты</b>\n\n"
        "Нужна помощь в заполнении анкеты на визу?\n\n"
        "✅ Наши специалисты помогут:\n"
        "• Правильно заполнить анкету\n"
        "• Подготовить документы\n"
        "• Подать заявление\n\n"
        "👇 Обратитесь к нам:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📝 Anketa to'ldirish" if uz else "📝 Заполнить анкету",
            url="https://t.me/AVIAKASSA9094"
        )],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_visa_{lang}"
        )],
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("visa_turkmen_"))
async def visa_turkmen(cb: CallbackQuery):
    lang = cb.data.split("_")[2]
    uz = lang == "uz"
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
        "🏛 Sankt-Peterburgdagi O'zbekiston Elchixonasi bilan "
        "bog'lanishingiz yoki bizga murojaat qilishingiz mumkin.\n\n"
        "👇 Bog'lanish uchun bosing:"
        if uz else
        "🇹🇲 <b>Виза Узбекистана для граждан Туркменистана</b>\n\n"
        "Оказываем полную помощь гражданам Туркменистана "
        "в оформлении визы в Узбекистан.\n\n"
        "📋 <b>Необходимые документы:</b>\n"
        "• Паспорт (действителен минимум 6 месяцев)\n"
        "• 2 фотографии 3×4\n"
        "• Заполненная анкета\n"
        "• Приглашение или бронь отеля\n"
        "• Консульский сбор\n\n"
        "🏛 Можете обратиться в Консульство Узбекистана "
        "в Санкт-Петербурге или к нам напрямую.\n\n"
        "👇 Нажмите для связи:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📞 Bog'lanish" if uz else "📞 Связаться",
            url="https://t.me/OMAD_TOUR9094"
        )],
        [InlineKeyboardButton(
            text="🏛 Konsulstvo guruhi" if uz else "🏛 Группа консульства",
            url="https://t.me/+i8I6ByH_CUVhOWQy"
        )],
        [InlineKeyboardButton(
            text="⬅️ Ortga" if uz else "⬅️ Назад",
            callback_data=f"go_visa_{lang}"
        )],
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  SAVOL — foydalanuvchi
# ═══════════════════════════════════════════════════════════════
@dp.message(S.question)
async def receive_question(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user = msg.from_user
    uname = f"@{user.username}" if user.username else "—"

    # Admin ga sarlavha
    header = (
        f"📨 <b>Yangi savol keldi!</b>\n\n"
        f"👤 Ism: <b>{user.full_name}</b>\n"
        f"📱 Username: {uname}\n"
        f"🆔 ID: <code>{user.id}</code>"
    )
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_{user.id}")]
    ])
    await bot.send_message(ADMIN_ID, header, reply_markup=reply_kb, parse_mode="HTML")

    # Xabarni adminga yuborish (asl ko'rinishda)
    if msg.text:
        await bot.send_message(ADMIN_ID, f"💬 <b>Savol:</b>\n\n{msg.text}", parse_mode="HTML")
    elif msg.photo:
        await bot.send_photo(ADMIN_ID, msg.photo[-1].file_id,
                             caption=f"🖼 <b>Rasm:</b>\n{msg.caption or ''}", parse_mode="HTML")
    elif msg.video:
        await bot.send_video(ADMIN_ID, msg.video.file_id,
                             caption=f"🎥 <b>Video:</b>\n{msg.caption or ''}", parse_mode="HTML")
    elif msg.document:
        await bot.send_document(ADMIN_ID, msg.document.file_id,
                                caption=f"📄 <b>Fayl:</b>\n{msg.caption or ''}", parse_mode="HTML")
    elif msg.voice:
        await bot.send_voice(ADMIN_ID, msg.voice.file_id)
        await bot.send_message(ADMIN_ID, "🎤 <b>Ovozli xabar</b>", parse_mode="HTML")
    elif msg.sticker:
        await bot.send_sticker(ADMIN_ID, msg.sticker.file_id)

    # Foydalanuvchiga tasdiqlash
    confirm = (
        "✅ <b>Murojaatingiz qabul qilindi!</b>\n\nIltimos javobni kuting 🙏"
        if lang == "uz" else
        "✅ <b>Ваш запрос принят!</b>\n\nПожалуйста, ожидайте ответа 🙏"
    )
    await msg.answer(confirm, reply_markup=kb_main(lang), parse_mode="HTML")
    await state.clear()

# ═══════════════════════════════════════════════════════════════
#  JAVOB — admin foydalanuvchiga javob beradi
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data.startswith("reply_"))
async def start_reply(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    user_id = int(cb.data.split("_")[1])
    await state.update_data(reply_to=user_id)
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
        await msg.answer("✅ Javob yuborildi!", reply_markup=kb_admin_main())
    except Exception as e:
        await msg.answer(f"❌ Xato: {e}")
    await state.clear()

# ═══════════════════════════════════════════════════════════════
#  ADMIN — statistika
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "adm_stats")
async def adm_stats(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    users  = load_users()
    total  = len(users)
    visits = sum(u["visits"] for u in users.values())
    lines  = [f"📊 <b>Statistika</b>\n",
              f"👥 Foydalanuvchilar: <b>{total}</b>",
              f"🔢 Jami tashriflar: <b>{visits}</b>\n",
              "<b>So'nggi 20 ta:</b>"]
    for i, (_, u) in enumerate(list(users.items())[-20:], 1):
        uname = f"@{u['username']}" if u.get("username") else "—"
        lines.append(f"{i}. {u['full_name']} {uname} — {u['visits']}x")
    await cb.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="adm_back")]
        ]),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
#  ADMIN — reklama
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.answer(
        "📢 <b>Reklama yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni yozing.\n"
        "Matn, rasm, video yoki fayl bo'lishi mumkin:",
        parse_mode="HTML"
    )
    await state.set_state(S.broadcast)

@dp.message(S.broadcast)
async def do_broadcast(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    users   = load_users()
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
#  ADMIN — narxlar
# ═══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "adm_back")
async def adm_back(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text("🔧 <b>Admin panel</b>", reply_markup=kb_admin_main(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_prices")
async def adm_prices(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.edit_text("💰 <b>Narxlar boshqaruvi</b>", reply_markup=kb_admin_prices(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_list")
async def adm_list(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["📋 <b>Joriy narxlar:</b>\n"]
    for i, (d, p) in enumerate(prices.items(), 1):
        lines.append(f"{i}. {d}\n   💰 {p:,} ₽  →  mijoz: {p+SBOR:,} ₽\n")
    await cb.message.edit_text("\n".join(lines), reply_markup=kb_admin_prices(), parse_mode="HTML")

@dp.callback_query(F.data == "adm_add")
async def adm_add(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.answer(
        "➕ Yangi yo'nalish nomini yozing:\n"
        "<i>Masalan: Санкт-Петербург → Навои</i>",
        parse_mode="HTML"
    )
    await state.set_state(S.add_dir)

@dp.message(S.add_dir)
async def adm_add_dir(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    await state.update_data(direction=msg.text)
    await msg.answer(f"✅ Yo'nalish: <b>{msg.text}</b>\n\nNarxni kiriting (sborsiz):", parse_mode="HTML")
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
            f"✅ <b>Saqlandi!</b>\n📍 {d}\n💰 Asl: {price:,} ₽  |  Mijoz: {price+SBOR:,} ₽",
            reply_markup=kb_admin_prices(), parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting! Masalan: 18500")

@dp.callback_query(F.data == "adm_edit")
async def adm_edit(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["✏️ Qaysi yo'nalishni o'zgartirish?\nRaqamini yozing:\n"]
    for i, (d, p) in enumerate(prices.items(), 1):
        lines.append(f"{i}. {d} — {p:,} ₽")
    await cb.message.answer("\n".join(lines))
    await state.set_state(S.edit_select)

@dp.message(S.edit_select)
async def adm_edit_select(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        idx = int(msg.text.strip()) - 1
        directions = list(load_prices().keys())
        if not (0 <= idx < len(directions)):
            await msg.answer("❌ Noto'g'ri raqam!")
            return
        await state.update_data(direction=directions[idx])
        await msg.answer(f"✏️ <b>{directions[idx]}</b>\n\nYangi narxni kiriting (sborsiz):", parse_mode="HTML")
        await state.set_state(S.edit_price)
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting!")

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
            f"✅ Yangilandi!\n📍 {d}\n💰 {price:,} ₽  →  {price+SBOR:,} ₽",
            reply_markup=kb_admin_prices(), parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting!")

@dp.callback_query(F.data == "adm_delete")
async def adm_delete(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    prices = load_prices()
    lines  = ["🗑 Qaysi yo'nalishni o'chirish?\nRaqamini yozing:\n"]
    for i, (d, p) in enumerate(prices.items(), 1):
        lines.append(f"{i}. {d} — {p:,} ₽")
    await cb.message.answer("\n".join(lines))
    await state.set_state(S.delete_select)

@dp.message(S.delete_select)
async def adm_delete_select(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        idx        = int(msg.text.strip()) - 1
        prices     = load_prices()
        directions = list(prices.keys())
        if not (0 <= idx < len(directions)):
            await msg.answer("❌ Noto'g'ri raqam!")
            return
        d = directions[idx]
        del prices[d]
        save_prices(prices)
        await msg.answer(f"✅ O'chirildi:\n{d}", reply_markup=kb_admin_prices())
        await state.clear()
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting!")

# ═══════════════════════════════════════════════════════════════
#  ISHGA TUSHIRISH
# ═══════════════════════════════════════════════════════════════
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
