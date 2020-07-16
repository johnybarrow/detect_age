import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = open('TOKEN').read()

bot = Bot(token=TOKEN)
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)
logging.basicConfig(level=logging.INFO)
