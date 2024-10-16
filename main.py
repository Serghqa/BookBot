import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_config
from keyboards import set_main_menu
from handlers import router
from config_logger import CONFIG_LOGGER
from functions import DatabaseMiddleware


logging.config.dictConfig(CONFIG_LOGGER)
logger = logging.getLogger(__name__)


async def main():
    logger.info('Start bot')
    config = load_config()
    redis = Redis(host='localhost')
    storage = RedisStorage(redis=redis)
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)
    await set_main_menu(bot)
    dp.include_router(router)
    router.message.middleware(DatabaseMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
