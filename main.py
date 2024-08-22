import logging
from aiogram.utils import executor

from components.keyboards import *
from components.database import *
from components.chatGPTresp import *
from components.bot import *

def main():
    logging.info("starting")
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()