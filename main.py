import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Ma'lumotlar
API_TOKEN = '8792355224:AAHvqotc-jeby0QFdrrxyuzWMBP6OwF1fvQ'
ADMIN_ID = 8158481112

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Holatlar (States)
class AdState(StatesGroup):
    contact = State()
    category = State()
    name = State()
    description = State()
    price = State()
    old_price = State()
    monthly = State()
    photo = State()

# Tugmalar
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Mahsulot qo'shish ➕")]], resize_keyboard=True)

def category_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Telefon"), KeyboardButton(text="Kompyuter")],
        [KeyboardButton(text="Boshqa")]
    ], resize_keyboard=True)

# Botni boshlash
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Xush kelibsiz! E'lon berish uchun tugmani bosing.", reply_markup=main_menu())

@dp.message(F.text == "Mahsulot qo'shish ➕")
async def add_product(message: types.Message, state: FSMContext):
    await state.set_state(AdState.contact)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Kontaktni yuborish", request_contact=True)]], resize_keyboard=True)
    await message.answer("1. Kontaktni yuboring:", reply_markup=kb)

@dp.message(AdState.contact)
async def get_contact(message: types.Message, state: FSMContext):
    contact = message.contact.phone_number if message.contact else message.text
    await state.update_data(contact=contact)
    await state.set_state(AdState.category)
    await message.answer("2. Mahsulot turini tanlang:", reply_markup=category_menu())

@dp.message(AdState.category)
async def get_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AdState.name)
    await message.answer("3. Mahsulot nomi:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(AdState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdState.description)
    await message.answer("4. Mahsulot haqida ma'lumot:")

@dp.message(AdState.description)
async def get_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdState.price)
    await message.answer("5. Narxi:")

@dp.message(AdState.price)
async def get_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AdState.old_price)
    await message.answer("6. Oldingi narxi:")

@dp.message(AdState.old_price)
async def get_old_price(message: types.Message, state: FSMContext):
    await state.update_data(old_price=message.text)
    await state.set_state(AdState.monthly)
    await message.answer("7. Oyiga to'lov summasi:")

@dp.message(AdState.monthly)
async def get_monthly(message: types.Message, state: FSMContext):
    await state.update_data(monthly=message.text)
    await state.set_state(AdState.photo)
    await message.answer("8. Mahsulot rasmini yuboring:")

@dp.message(AdState.photo, F.photo)
async def get_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    
    caption = (f"Yangi e'lon!\n\n👤 Kontakt: {data['contact']}\n🗂 Tur: {data['category']}\n"
               f"📦 Nomi: {data['name']}\n📝 Haqida: {data['description']}\n"
               f"💰 Narxi: {data['price']}\n❌ Eski narxi: {data['old_price']}\n"
               f"🗓 Oyiga: {data['monthly']}")

    # Admin uchun tugmalar
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{message.from_user.id}"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"reject_{message.from_user.id}")]
    ])

    await bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=admin_kb)
    await message.answer("Rahmat! E'loningiz 24 soat ichida ko'rib chiqiladi.", reply_markup=main_menu())
    await state.clear()

# Admin qarori
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def process_decision(callback: types.CallbackQuery):
    action, user_id = callback.data.split("_")
    if action == "accept":
        await bot.send_message(user_id, "Sizning e'loningiz qabul qilindi! ✅")
        await callback.answer("Qabul qilindi")
    else:
        await bot.send_message(user_id, "Sizning e'loningiz bekor qilindi. ❌")
        await callback.answer("Bekor qilindi")
    await callback.message.delete()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())