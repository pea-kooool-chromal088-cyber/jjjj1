#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram-бот для регистрации на мероприятия
"""

import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import TELEGRAM_BOT_TOKEN
from database import Database
from registration import RegistrationHandler
from constants import NAME, EMAIL, PHONE, BIRTH_DATE, CONFIRM

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Инициализация базы данных
    db = Database("registrations.db")
    
    # Создание экземпляра RegistrationHandler
    reg_handler = RegistrationHandler(db)
    
    # Создание приложения
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Создание ConversationHandler для регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', reg_handler.register_command)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_handler.get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_handler.get_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_handler.get_phone)],
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_handler.get_birth_date)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_handler.confirm_registration)]
        },
        fallbacks=[CommandHandler('cancel', reg_handler.cancel_registration)]
    )
    
    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", reg_handler.start_command))
    application.add_handler(CommandHandler("help", reg_handler.help_command))
    application.add_handler(CommandHandler("my_info", reg_handler.my_info_command))
    application.add_handler(CommandHandler("admin", reg_handler.admin_command))
    application.add_handler(CommandHandler("stats", reg_handler.stats_command))
    application.add_handler(CommandHandler("new_event", reg_handler.new_event_command))
    
    # Добавление ConversationHandler в приложение
    application.add_handler(conv_handler)
    
    # Запуск бота
    logger.info("Запуск Telegram-бота...")
    application.run_polling()

if __name__ == '__main__':
    main()