#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестирование Telegram-бота регистрации на мероприятия через Pyrogram
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import TELEGRAM_BOT_TOKEN

# Ваши учетные данные для входа в аккаунт Telegram
API_ID = "YOUR_API_ID"  # Замените на ваш API ID
API_HASH = "YOUR_API_HASH"  # Замените на ваш API HASH
PHONE_NUMBER = "YOUR_PHONE_NUMBER"  # Замените на ваш номер телефона

# ID бота, которого будем тестировать
BOT_USERNAME = "YOUR_BOT_USERNAME"  # Замените на юзернейм вашего бота

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_test_messages():
    """Функция для отправки тестовых сообщений боту"""
    # Создаем клиент для подключения к вашему аккаунту Telegram
    async with Client("test_account", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER) as app:
        logger.info("Подключено к Telegram аккаунту")
        
        # Отправляем команду /start боту
        logger.info(f"Отправляем команду /start боту @{BOT_USERNAME}")
        await app.send_message(BOT_USERNAME, "/start")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(2)
        
        # Отправляем команду /register для начала регистрации
        logger.info(f"Отправляем команду /register боту @{BOT_USERNAME}")
        await app.send_message(BOT_USERNAME, "/register")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(2)
        
        # Отправляем тестовое имя
        logger.info("Отправляем тестовое имя")
        await app.send_message(BOT_USERNAME, "Иван Иванов")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(2)
        
        # Отправляем тестовый email
        logger.info("Отправляем тестовый email")
        await app.send_message(BOT_USERNAME, "ivan@example.com")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(2)
        
        # Отправляем тестовый номер телефона
        logger.info("Отправляем тестовый номер телефона")
        await app.send_message(BOT_USERNAME, "+79991234567")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(2)
        
        # Отправляем тестовую дату рождения
        logger.info("Отправляем тестовую дату рождения")
        await app.send_message(BOT_USERNAME, "01.01.1990")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(2)
        
        # Подтверждаем регистрацию
        logger.info("Подтверждаем регистрацию")
        await app.send_message(BOT_USERNAME, "✅ Подтвердить")
        
        logger.info("Тестовые сообщения отправлены успешно!")

async def check_bot_response():
    """Функция для проверки ответов бота"""
    # Создаем клиент для подключения к вашему аккаунту Telegram
    async with Client("test_account", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER) as app:
        logger.info("Подключено к Telegram аккаунту для проверки ответов")
        
        # Отправляем команду /my_info для проверки информации
        logger.info(f"Отправляем команду /my_info боту @{BOT_USERNAME}")
        await app.send_message(BOT_USERNAME, "/my_info")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(3)
        
        # Отправляем команду /help
        logger.info(f"Отправляем команду /help боту @{BOT_USERNAME}")
        await app.send_message(BOT_USERNAME, "/help")
        
        # Ждем немного, чтобы получить ответ
        await asyncio.sleep(2)
        
        logger.info("Проверка ответов бота завершена!")

async def admin_test():
    """Функция для тестирования админ-команд"""
    # Создаем клиент для подключения к вашему аккаунту Telegram
    async with Client("test_account", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER) as app:
        logger.info("Подключено к Telegram аккаунту для тестирования админ-функций")
        
        # Проверяем, является ли наш аккаунт администратором
        logger.info(f"Отправляем команду /admin боту @{BOT_USERNAME}")
        await app.send_message(BOT_USERNAME, "/admin")
        
        await asyncio.sleep(2)
        
        # Проверяем статистику (если аккаунт является администратором)
        logger.info(f"Отправляем команду /stats боту @{BOT_USERNAME}")
        await app.send_message(BOT_USERNAME, "/stats")
        
        await asyncio.sleep(2)
        
        logger.info("Тестирование админ-функций завершено!")

def main():
    """Основная функция для запуска тестов"""
    print("Выберите тип теста:")
    print("1. Тестирование регистрации")
    print("2. Проверка ответов бота")
    print("3. Тестирование админ-функций")
    print("4. Полное тестирование")
    
    choice = input("Введите номер теста (1-4): ")
    
    if choice == "1":
        asyncio.run(send_test_messages())
    elif choice == "2":
        asyncio.run(check_bot_response())
    elif choice == "3":
        asyncio.run(admin_test())
    elif choice == "4":
        print("Запуск полного тестирования...")
        asyncio.run(send_test_messages())
        print("\nОжидание 5 секунд перед следующим тестом...")
        asyncio.sleep(5)
        asyncio.run(check_bot_response())
        print("\nОжидание 5 секунд перед следующим тестом...")
        asyncio.sleep(5)
        asyncio.run(admin_test())
        print("\nПолное тестирование завершено!")
    else:
        print("Неверный выбор. Пожалуйста, выберите номер от 1 до 4.")

if __name__ == "__main__":
    main()