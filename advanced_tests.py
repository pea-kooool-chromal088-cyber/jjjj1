#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Расширенные тесты для Telegram-бота регистрации на мероприятия
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import os
from datetime import datetime

from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes
from config import DATABASE_PATH
from database import Database
from registration import RegistrationHandler
from constants import *

class TestRegistrationHandler(unittest.TestCase):
    def setUp(self):
        """Настройка тестов"""
        self.db = Database(DATABASE_PATH)
        self.reg_handler = RegistrationHandler(self.db)
        
        # Создаем mock объекты для тестирования
        self.mock_update = AsyncMock(spec=Update)
        self.mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        self.mock_user = AsyncMock(spec=User)
        self.mock_user.id = 123456789
        self.mock_user.first_name = "Test"
        self.mock_user.last_name = "User"
        self.mock_message = AsyncMock(spec=Message)
        self.mock_chat = AsyncMock(spec=Chat)
        
        self.mock_update.effective_user = self.mock_user
        self.mock_update.message = self.mock_message
        self.mock_update.effective_chat = self.mock_chat
        
        # Очищаем пользовательские данные для тестов
        self.mock_context.user_data = {}
    
    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем тестового пользователя из базы данных
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE telegram_id = ?", (self.mock_user.id,))
        conn.commit()
        conn.close()
    
    @patch('telegram.Message.reply_text')
    async def test_start_command(self, mock_reply):
        """Тест команды /start"""
        mock_reply.return_value = None
        self.mock_update.message.text = '/start'
        
        await self.reg_handler.start_command(self.mock_update, self.mock_context)
        
        mock_reply.assert_called_once()
        # Проверяем, что было отправлено приветственное сообщение
        args, kwargs = mock_reply.call_args
        self.assertIn('Добро пожаловать', args[0])
    
    @patch('telegram.Message.reply_text')
    async def test_help_command(self, mock_reply):
        """Тест команды /help"""
        mock_reply.return_value = None
        self.mock_update.message.text = '/help'
        
        await self.reg_handler.help_command(self.mock_update, self.mock_context)
        
        mock_reply.assert_called_once()
        # Проверяем, что было отправлено сообщение помощи
        args, kwargs = mock_reply.call_args
        self.assertIn('Бот для регистрации', args[0])
    
    @patch('telegram.Message.reply_text')
    async def test_register_already_registered(self, mock_reply):
        """Тест попытки повторной регистрации"""
        # Сначала зарегистрируем пользователя
        self.db.add_user(
            telegram_id=self.mock_user.id,
            full_name="Test User",
            email="test@example.com",
            phone="+79991234567",
            birth_date="01.01.1990"
        )
        
        mock_reply.return_value = None
        
        await self.reg_handler.register_command(self.mock_update, self.mock_context)
        
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('уже зарегистрированы', args[0])
    
    @patch('telegram.Message.reply_text')
    async def test_get_name_cancel(self, mock_reply):
        """Тест отмены ввода имени"""
        mock_reply.return_value = None
        self.mock_update.message.text = CANCEL_BUTTON
        
        result = await self.reg_handler.get_name(self.mock_update, self.mock_context)
        
        self.assertEqual(result, ConversationHandler.END)
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('Регистрация отменена', args[0])
    
    @patch('telegram.Message.reply_text')
    async def test_get_name_valid(self, mock_reply):
        """Тест ввода корректного имени"""
        mock_reply.return_value = None
        self.mock_update.message.text = "Иван Петров"
        
        result = await self.reg_handler.get_name(self.mock_update, self.mock_context)
        
        self.assertEqual(result, EMAIL)
        self.assertEqual(self.mock_context.user_data['full_name'], "Иван Петров")
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('email', args[0].lower())
    
    @patch('telegram.Message.reply_text')
    async def test_get_email_cancel(self, mock_reply):
        """Тест отмены ввода email"""
        mock_reply.return_value = None
        self.mock_update.message.text = CANCEL_BUTTON
        
        result = await self.reg_handler.get_email(self.mock_update, self.mock_context)
        
        self.assertEqual(result, ConversationHandler.END)
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('Регистрация отменена', args[0])
    
    @patch('telegram.Message.reply_text')
    async def test_get_email_invalid(self, mock_reply):
        """Тест ввода некорректного email"""
        mock_reply.return_value = None
        self.mock_update.message.text = "invalid-email"
        
        result = await self.reg_handler.get_email(self.mock_update, self.mock_context)
        
        self.assertEqual(result, EMAIL)
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('некорректный email', args[0].lower())
    
    @patch('telegram.Message.reply_text')
    async def test_get_email_valid(self, mock_reply):
        """Тест ввода корректного email"""
        mock_reply.return_value = None
        self.mock_update.message.text = "test@example.com"
        
        result = await self.reg_handler.get_email(self.mock_update, self.mock_context)
        
        self.assertEqual(result, PHONE)
        self.assertEqual(self.mock_context.user_data['email'], "test@example.com")
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('номер телефона', args[0].lower())
    
    @patch('telegram.Message.reply_text')
    async def test_get_phone_cancel(self, mock_reply):
        """Тест отмены ввода телефона"""
        mock_reply.return_value = None
        self.mock_update.message.text = CANCEL_BUTTON
        
        result = await self.reg_handler.get_phone(self.mock_update, self.mock_context)
        
        self.assertEqual(result, ConversationHandler.END)
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('Регистрация отменена', args[0])
    
    @patch('telegram.Message.reply_text')
    async def test_get_phone_invalid(self, mock_reply):
        """Тест ввода некорректного номера телефона"""
        mock_reply.return_value = None
        self.mock_update.message.text = "invalid-phone"
        
        result = await self.reg_handler.get_phone(self.mock_update, self.mock_context)
        
        self.assertEqual(result, PHONE)
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('некорректный номер', args[0].lower())
    
    @patch('telegram.Message.reply_text')
    async def test_get_phone_valid(self, mock_reply):
        """Тест ввода корректного номера телефона"""
        mock_reply.return_value = None
        self.mock_update.message.text = "+79991234567"
        
        result = await self.reg_handler.get_phone(self.mock_update, self.mock_context)
        
        self.assertEqual(result, BIRTH_DATE)
        self.assertEqual(self.mock_context.user_data['phone'], "+79991234567")
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('дату рождения', args[0].lower())
    
    @patch('telegram.Message.reply_text')
    async def test_get_birth_date_cancel(self, mock_reply):
        """Тест отмены ввода даты рождения"""
        mock_reply.return_value = None
        self.mock_update.message.text = CANCEL_BUTTON
        
        result = await self.reg_handler.get_birth_date(self.mock_update, self.mock_context)
        
        self.assertEqual(result, ConversationHandler.END)
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('Регистрация отменена', args[0])
    
    @patch('telegram.Message.reply_text')
    async def test_get_birth_date_invalid_format(self, mock_reply):
        """Тест ввода даты рождения в неправильном формате"""
        mock_reply.return_value = None
        self.mock_update.message.text = "32.13.1990"  # Несуществующая дата
        
        result = await self.reg_handler.get_birth_date(self.mock_update, self.mock_context)
        
        self.assertEqual(result, BIRTH_DATE)
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('некорректная дата', args[0].lower())
    
    @patch('telegram.Message.reply_text')
    async def test_get_birth_date_future_date(self, mock_reply):
        """Тест ввода даты рождения в будущем"""
        mock_reply.return_value = None
        # Дата рождения в будущем
        future_date = (datetime.now().date().replace(year=datetime.now().date().year + 1)).strftime("%d.%m.%Y")
        self.mock_update.message.text = future_date
        
        result = await self.reg_handler.get_birth_date(self.mock_update, self.mock_context)
        
        self.assertEqual(result, BIRTH_DATE)
        mock_reply.assert_called()
        # Проверяем, что есть сообщение о будущей дате
        called_args = mock_reply.call_args_list
        found_future_error = False
        for call in called_args:
            if 'будущем' in call[0][0]:
                found_future_error = True
                break
        self.assertTrue(found_future_error)
    
    @patch('telegram.Message.reply_text')
    async def test_get_birth_date_valid(self, mock_reply):
        """Тест ввода корректной даты рождения"""
        mock_reply.return_value = None
        self.mock_update.message.text = "01.01.1990"
        
        # Устанавливаем необходимые данные пользователя
        self.mock_context.user_data['full_name'] = "Test User"
        self.mock_context.user_data['email'] = "test@example.com"
        self.mock_context.user_data['phone'] = "+79991234567"
        
        result = await self.reg_handler.get_birth_date(self.mock_update, self.mock_context)
        
        self.assertEqual(result, CONFIRM)
        self.assertEqual(self.mock_context.user_data['birth_date'], "01.01.1990")
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        self.assertIn('подтвердите', args[0].lower())
        self.assertIn('данные', args[0].lower())

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Настройка тестов для базы данных"""
        self.test_db_path = "test_registrations.db"
        self.db = Database(self.test_db_path)
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_add_user(self):
        """Тест добавления пользователя"""
        user_id = self.db.add_user(
            telegram_id=123456789,
            full_name="Test User",
            email="test@example.com",
            phone="+79991234567",
            birth_date="01.01.1990"
        )
        
        self.assertIsNotNone(user_id)
        
        # Проверяем, что пользователь действительно добавлен
        user = self.db.get_user_by_telegram_id(123456789)
        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], "Test User")
        self.assertEqual(user['email'], "test@example.com")
        self.assertEqual(user['phone'], "+79991234567")
        self.assertEqual(user['birth_date'], "01.01.1990")
    
    def test_get_nonexistent_user(self):
        """Тест получения несуществующего пользователя"""
        user = self.db.get_user_by_telegram_id(999999999)
        self.assertIsNone(user)
    
    def test_add_duplicate_user(self):
        """Тест добавления дублирующегося пользователя"""
        # Добавляем пользователя первый раз
        user_id1 = self.db.add_user(
            telegram_id=123456789,
            full_name="Test User",
            email="test@example.com",
            phone="+79991234567",
            birth_date="01.01.1990"
        )
        
        self.assertIsNotNone(user_id1)
        
        # Пробуем добавить того же пользователя снова
        user_id2 = self.db.add_user(
            telegram_id=123456789,
            full_name="Test User Updated",
            email="updated@example.com",
            phone="+79997654321",
            birth_date="02.02.1992"
        )
        
        # Должно вернуть None, так как пользователь с таким telegram_id уже существует
        self.assertIsNone(user_id2)
        
        # Проверяем, что в базе остался только первый вариант
        user = self.db.get_user_by_telegram_id(123456789)
        self.assertEqual(user['full_name'], "Test User")
        self.assertEqual(user['email'], "test@example.com")
    
    def test_get_registration_stats(self):
        """Тест получения статистики регистрации"""
        # Добавляем нескольких пользователей
        self.db.add_user(
            telegram_id=111111111,
            full_name="User One",
            email="one@example.com",
            phone="+79991111111",
            birth_date="01.01.1990"
        )
        
        self.db.add_user(
            telegram_id=222222222,
            full_name="User Two",
            email="two@example.com",
            phone="+79992222222",
            birth_date="02.02.1992"
        )
        
        stats = self.db.get_registration_stats()
        
        self.assertEqual(stats['total_users'], 2)
        # У нас пока нет мероприятий, так что остальные значения должны быть 0
        self.assertEqual(stats['total_events'], 0)
        self.assertEqual(stats['total_registrations'], 0)

class TestConstants(unittest.TestCase):
    def test_constants_defined(self):
        """Тест наличия всех необходимых констант"""
        # Проверяем, что все необходимые константы определены
        self.assertIsInstance(WELCOME_MESSAGE, str)
        self.assertIsInstance(HELP_MESSAGE, str)
        self.assertIsInstance(NAME_REQUEST, str)
        self.assertIsInstance(EMAIL_REQUEST, str)
        self.assertIsInstance(PHONE_REQUEST, str)
        self.assertIsInstance(BIRTH_DATE_REQUEST, str)
        self.assertIsInstance(REGISTRATION_SUCCESS, str)
        self.assertIsInstance(INVALID_EMAIL, str)
        self.assertIsInstance(INVALID_PHONE, str)
        self.assertIsInstance(INVALID_DATE, str)
        self.assertIsInstance(CANCEL_BUTTON, str)
        self.assertIsInstance(CONFIRM_BUTTON, str)
        
        # Проверяем, что константы не пустые
        self.assertTrue(len(WELCOME_MESSAGE) > 0)
        self.assertTrue(len(HELP_MESSAGE) > 0)
        self.assertTrue(len(NAME_REQUEST) > 0)
        self.assertTrue(len(EMAIL_REQUEST) > 0)

def run_tests():
    """Запуск всех тестов"""
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    import sys
    import sqlite3
    
    print("Запуск расширенных тестов для Telegram-бота регистрации на мероприятия...")
    success = run_tests()
    
    if success:
        print("\n✅ Все тесты пройдены успешно!")
    else:
        print("\n❌ Некоторые тесты не пройдены!")
    
    sys.exit(0 if success else 1)