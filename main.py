from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from handlers import handlers, handlers_auth
from handlers import handlers_context, handlers_new_context

env = Env()
env.read_env('../env/.env')

TELEGRAM_TOKEN = env('TELEGRAM_TOKEN')

redis: Redis = Redis(host='localhost')
storage: RedisStorage = RedisStorage(redis=redis)


# Создаем объекты бота и диспетчера
dp = Dispatcher(storage=storage)
dp.include_router(handlers_context.router)
dp.include_router(handlers_new_context.router)
dp.include_router(handlers_auth.router)
dp.include_router(handlers.router)

bot: Bot = Bot(TELEGRAM_TOKEN)  # , parse_mode='MarkdownV2'


# Запускаем поллинг
if __name__ == '__main__':
    bot.delete_webhook(drop_pending_updates=True)
    dp.run_polling(bot)
