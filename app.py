import logging
from os import getenv
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ContentType, BotCommand
from pathlib import Path
from model.model import predict_class

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(find_dotenv())

# FSM для отслеживания состояния пользователя
class SendPhoto(StatesGroup):
    waiting_for_photo = State()

token = getenv('TOKEN')
bot = Bot(token=token)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO, filename='bot_model_cv_yolo.log')

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запустить бота'),
    ]
    await bot.set_my_commands(main_menu_commands)

@dp.message(Command(commands=['start']))
async def proccess_command_start(message: Message):
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    text = f'Привет, {user_name}! Вы запустили бота по определению рыбок: LionFish и BunnerFish. Отправьте нам фото.'
    logging.info(f'User:{user_name} id:{user_id} запустил бота')
    await bot.send_message(chat_id=user_id, text=text)


async def photo(message: Message):
    user_name = message.from_user.full_name
    user_id = message.from_user.id

    photo = message.photo[-1]
    file_id = photo.file_id
    file_name = f"user_photo_{user_id}.jpg"

    await bot.download(file_id, destination=file_name)

    logging.info(f"User {user_name} ({user_id}) sent a photo: {file_name}")

    try:
        _, proc_time, res_image = predict_class(file_name)
    except Exception as exc:
        logging.error(f"Error with processing image for {user_id} -- {user_name}: {exc}")
        await message.reply('Произошла ошибка при обработке изображения. Попробуйте ещё раз или отправьте другую картинку')
        return

    await message.reply(f"Время работы: {proc_time} секунд")
    result_image_file = FSInputFile(res_image)
    await bot.send_photo(chat_id=user_id, photo=result_image_file)

dp.message.register(proccess_command_start, Command(commands=['start']))
dp.message.register(photo, F.content_type == ContentType.PHOTO)

if __name__ == '__main__':
    dp.startup.register(set_main_menu)
    dp.run_polling(bot)
