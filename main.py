from environs import Env
from aiogram import Bot
from handlers.handlers import dp

env = Env()
env.read_env('../env/.env')

TELEGRAM_TOKEN = env('TELEGRAM_TOKEN')


# Создаем объекты бота и диспетчера
bot: Bot = Bot(TELEGRAM_TOKEN)

# Запускаем поллинг
if __name__ == '__main__':
    bot.delete_webhook(drop_pending_updates=True)
    dp.run_polling(bot)