#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тесты для Telegram-бота регистрации на мероприятия с использованием pytest
"""

import asyncio
import pytest
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

@pytest.fixture
def mock_update():
    """Фикстура для создания mock объекта Update"""
    mock_update = AsyncMock(spec=Update)
    mock_user = AsyncMock(spec=User)
    mock_user.id = 123456789
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_message = AsyncMock(spec=Message)
    mock_chat = AsyncMock(spec=Chat)
    
    mock_update.effective_user = mock_user
    mock_update.message = mock_message
    mock_update.effective_chat = mock_chat
    
    return mock_update

@pytest.fixture
def mock_context():
    """Фикстура для создания mock объекта Context"""
    mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    mock_context.user_data = {}
    return mock_context

@pytest.fixture
def db():
    """Фикстура для создания тестовой базы данных"""
    test_db_path = "test_registrations.db"
    database = Database(test_db_path)
    yield database
    # Удаляем тестовую базу данных после тестов
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def reg_handler(db):
    """Фикстура для создания обработчика регистрации"""
    return RegistrationHandler(db)

@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context, reg_handler):
    """Тест команды /start"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = '/start'
        
        await reg_handler.start_command(mock_update, mock_context)
        
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'Добро пожаловать' in args[0]

@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context, reg_handler):
    """Тест команды /help"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = '/help'
        
        await reg_handler.help_command(mock_update, mock_context)
        
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'Бот для регистрации' in args[0]

@pytest.mark.asyncio
async def test_register_already_registered(mock_update, mock_context, reg_handler, db):
    """Тест попытки повторной регистрации"""
    # Сначала зарегистрируем пользователя
    db.add_user(
        telegram_id=mock_update.effective_user.id,
        full_name="Test User",
        email="test@example.com",
        phone="+79991234567",
        birth_date="01.01.1990"
    )
    
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        
        await reg_handler.register_command(mock_update, mock_context)
        
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'уже зарегистрированы' in args[0]

@pytest.mark.asyncio
async def test_get_name_cancel(mock_update, mock_context, reg_handler):
    """Тест отмены ввода имени"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = CANCEL_BUTTON
        
        result = await reg_handler.get_name(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'Регистрация отменена' in args[0]

@pytest.mark.asyncio
async def test_get_name_valid(mock_update, mock_context, reg_handler):
    """Тест ввода корректного имени"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = "Иван Петров"
        
        result = await reg_handler.get_name(mock_update, mock_context)
        
        assert result == EMAIL
        assert mock_context.user_data['full_name'] == "Иван Петров"
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'email' in args[0].lower()

@pytest.mark.asyncio
async def test_get_email_cancel(mock_update, mock_context, reg_handler):
    """Тест отмены ввода email"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = CANCEL_BUTTON
        
        result = await reg_handler.get_email(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'Регистрация отменена' in args[0]

@pytest.mark.asyncio
async def test_get_email_invalid(mock_update, mock_context, reg_handler):
    """Тест ввода некорректного email"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = "invalid-email"
        
        result = await reg_handler.get_email(mock_update, mock_context)
        
        assert result == EMAIL
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'некорректный email' in args[0].lower()

@pytest.mark.asyncio
async def test_get_email_valid(mock_update, mock_context, reg_handler):
    """Тест ввода корректного email"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = "test@example.com"
        
        result = await reg_handler.get_email(mock_update, mock_context)
        
        assert result == PHONE
        assert mock_context.user_data['email'] == "test@example.com"
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'номер телефона' in args[0].lower()

@pytest.mark.asyncio
async def test_get_phone_cancel(mock_update, mock_context, reg_handler):
    """Тест отмены ввода телефона"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = CANCEL_BUTTON
        
        result = await reg_handler.get_phone(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'Регистрация отменена' in args[0]

@pytest.mark.asyncio
async def test_get_phone_invalid(mock_update, mock_context, reg_handler):
    """Тест ввода некорректного номера телефона"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = "invalid-phone"
        
        result = await reg_handler.get_phone(mock_update, mock_context)
        
        assert result == PHONE
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'некорректный номер' in args[0].lower()

@pytest.mark.asyncio
async def test_get_phone_valid(mock_update, mock_context, reg_handler):
    """Тест ввода корректного номера телефона"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = "+79991234567"
        
        result = await reg_handler.get_phone(mock_update, mock_context)
        
        assert result == BIRTH_DATE
        assert mock_context.user_data['phone'] == "+79991234567"
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'дату рождения' in args[0].lower()

@pytest.mark.asyncio
async def test_get_birth_date_cancel(mock_update, mock_context, reg_handler):
    """Тест отмены ввода даты рождения"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = CANCEL_BUTTON
        
        result = await reg_handler.get_birth_date(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'Регистрация отменена' in args[0]

@pytest.mark.asyncio
async def test_get_birth_date_invalid_format(mock_update, mock_context, reg_handler):
    """Тест ввода даты рождения в неправильном формате"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = "32.13.1990"  # Несуществующая дата
        
        result = await reg_handler.get_birth_date(mock_update, mock_context)
        
        assert result == BIRTH_DATE
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'некорректная дата' in args[0].lower()

@pytest.mark.asyncio
async def test_get_birth_date_future_date(mock_update, mock_context, reg_handler):
    """Тест ввода даты рождения в будущем"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        # Дата рождения в будущем
        future_date = (datetime.now().date().replace(year=datetime.now().date().year + 1)).strftime("%d.%m.%Y")
        mock_update.message.text = future_date
        
        result = await reg_handler.get_birth_date(mock_update, mock_context)
        
        assert result == BIRTH_DATE
        # Проверяем, что есть сообщение о будущей дате
        mock_reply.assert_called()
        called_args = mock_reply.call_args_list
        found_future_error = False
        for call in called_args:
            if 'будущем' in call[0][0]:
                found_future_error = True
                break
        assert found_future_error

@pytest.mark.asyncio
async def test_get_birth_date_valid(mock_update, mock_context, reg_handler):
    """Тест ввода корректной даты рождения"""
    with patch.object(mock_update.message, 'reply_text') as mock_reply:
        mock_reply.return_value = None
        mock_update.message.text = "01.01.1990"
        
        # Устанавливаем необходимые данные пользователя
        mock_context.user_data['full_name'] = "Test User"
        mock_context.user_data['email'] = "test@example.com"
        mock_context.user_data['phone'] = "+79991234567"
        
        result = await reg_handler.get_birth_date(mock_update, mock_context)
        
        assert result == CONFIRM
        assert mock_context.user_data['birth_date'] == "01.01.1990"
        mock_reply.assert_called_once()
        args, kwargs = mock_reply.call_args
        assert 'подтвердите' in args[0].lower()
        assert 'данные' in args[0].lower()

def test_add_user(db):
    """Тест добавления пользователя"""
    user_id = db.add_user(
        telegram_id=123456789,
        full_name="Test User",
        email="test@example.com",
        phone="+79991234567",
        birth_date="01.01.1990"
    )
    
    assert user_id is not None
    
    # Проверяем, что пользователь действительно добавлен
    user = db.get_user_by_telegram_id(123456789)
    assert user is not None
    assert user['full_name'] == "Test User"
    assert user['email'] == "test@example.com"
    assert user['phone'] == "+79991234567"
    assert user['birth_date'] == "01.01.1990"

def test_get_nonexistent_user(db):
    """Тест получения несуществующего пользователя"""
    user = db.get_user_by_telegram_id(99999)
    assert user is None

def test_add_duplicate_user(db):
    """Тест добавления дублирующегося пользователя"""
    # Добавляем пользователя первый раз
    user_id1 = db.add_user(
        telegram_id=123456789,
        full_name="Test User",
        email="test@example.com",
        phone="+79991234567",
        birth_date="01.01.1990"
    )
    
    assert user_id1 is not None
    
    # Пробуем добавить того же пользователя снова
    user_id2 = db.add_user(
        telegram_id=123456789,
        full_name="Test User Updated",
        email="updated@example.com",
        phone="+79997654321",
        birth_date="02.02.1992"
    )
    
    # Должно вернуть None, так как пользователь с таким telegram_id уже существует
    assert user_id2 is None
    
    # Проверяем, что в базе остался только первый вариант
    user = db.get_user_by_telegram_id(123456789)
    assert user['full_name'] == "Test User"
    assert user['email'] == "test@example.com"

def test_get_registration_stats(db):
    """Тест получения статистики регистрации"""
    # Добавляем нескольких пользователей
    db.add_user(
        telegram_id=11111,
        full_name="User One",
        email="one@example.com",
        phone="+79991111111",
        birth_date="01.01.1990"
    )
    
    db.add_user(
        telegram_id=222222222,
        full_name="User Two",
        email="two@example.com",
        phone="+79992222222",
        birth_date="02.02.1992"
    )
    
    stats = db.get_registration_stats()
    
    assert stats['total_users'] == 2
    # У нас пока нет мероприятий, так что остальные значения должны быть 0
    assert stats['total_events'] == 0
    assert stats['total_registrations'] == 0

def test_constants_defined():
    """Тест наличия всех необходимых констант"""
    # Проверяем, что все необходимые константы определены
    assert isinstance(WELCOME_MESSAGE, str)
    assert isinstance(HELP_MESSAGE, str)
    assert isinstance(NAME_REQUEST, str)
    assert isinstance(EMAIL_REQUEST, str)
    assert isinstance(PHONE_REQUEST, str)
    assert isinstance(BIRTH_DATE_REQUEST, str)
    assert isinstance(REGISTRATION_SUCCESS, str)
    assert isinstance(INVALID_EMAIL, str)
    assert isinstance(INVALID_PHONE, str)
    assert isinstance(INVALID_DATE, str)
    assert isinstance(CANCEL_BUTTON, str)
    assert isinstance(CONFIRM_BUTTON, str)
    
    # Проверяем, что константы не пустые
    assert len(WELCOME_MESSAGE) > 0
    assert len(HELP_MESSAGE) > 0
    assert len(NAME_REQUEST) > 0
    assert len(EMAIL_REQUEST) > 0

if __name__ == '__main__':
    import sys
    
    print("Запуск тестов для Telegram-бота регистрации на мероприятия с использованием pytest...")
    exit_code = pytest.main([__file__, "-v"])
    sys.exit(exit_code)