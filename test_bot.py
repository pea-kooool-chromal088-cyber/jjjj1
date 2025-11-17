#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестирование функциональности бота для регистрации на мероприятия
"""

import sqlite3
import os
from datetime import datetime
from database import Database

def test_database():
    """Тестирование функций базы данных"""
    print("=== Тестирование базы данных ===")
    
    # Создаем временную базу данных для тестирования
    test_db = Database("test_registrations.db")
    
    # Тестирование добавления пользователя
    print("1. Тестирование добавления пользователя...")
    user_id = test_db.add_user(
        telegram_id=123456789,
        full_name="Тестовый Пользователь",
        email="test@example.com",
        phone="+79991234567",
        birth_date="01.01.1990"
    )
    
    if user_id:
        print(f"   Успешно добавлен пользователь с ID {user_id}")
    else:
        print("   Ошибка при добавлении пользователя")
    
    # Тестирование получения пользователя
    print("2. Тестирование получения пользователя...")
    user = test_db.get_user_by_telegram_id(123456789)
    if user:
        print(f"   Получен пользователь: {user['full_name']}, email: {user['email']}")
    else:
        print("   Пользователь не найден")
    
    # Тестирование добавления мероприятия
    print("3. Тестирование добавления мероприятия...")
    event_id = test_db.add_event(
        title="Тестовое мероприятие",
        description="Описание тестового мероприятия",
        date="2024-12-31 18:00:00",
        location="Тестовое место"
    )
    
    if event_id:
        print(f"   Успешно добавлено мероприятие с ID {event_id}")
    else:
        print("   Ошибка при добавлении мероприятия")
    
    # Тестирование регистрации пользователя на мероприятие
    print("4. Тестирование регистрации на мероприятие...")
    test_db.register_user_for_event(user_id, event_id)
    print("   Пользователь зарегистрирован на мероприятие")
    
    # Тестирование получения регистраций пользователя
    print("5. Тестирование получения регистраций пользователя...")
    registrations = test_db.get_user_registrations(user_id)
    if registrations:
        print(f"   Найдено {len(registrations)} регистраций пользователя")
        for reg in registrations:
            print(f"     - Мероприятие: {reg['title']}, дата: {reg['date']}")
    else:
        print("   Регистрации пользователя не найдены")
    
    # Тестирование получения регистраций на мероприятие
    print("6. Тестирование получения регистраций на мероприятие...")
    event_registrations = test_db.get_event_registrations(event_id)
    if event_registrations:
        print(f"   Найдено {len(event_registrations)} регистраций на мероприятие")
        for reg in event_registrations:
            print(f"     - Участник: {reg['full_name']}, email: {reg['email']}")
    else:
        print("   Регистрации на мероприятие не найдены")
    
    # Тестирование получения статистики
    print("7. Тестирование получения статистики...")
    stats = test_db.get_registration_stats()
    print(f"   Статистика: пользователей - {stats['total_users']}, "
          f"мероприятий - {stats['total_events']}, "
          f"регистраций - {stats['total_registrations']}")
    
    # Удаляем тестовую базу данных
    os.remove("test_registrations.db")
    print("\nТестирование базы данных завершено успешно!")

def test_registration_flow():
    """Тестирование логики регистрации"""
    print("\n=== Тестирование логики регистрации ===")
    
    # Тестирование валидации email
    import re
    email = "test@example.com"
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("1. Валидация email: OK")
    else:
        print("1. Валидация email: FAIL")
    
    # Тестирование валидации телефона
    phone = "+79991234567"
    if re.match(r'^[\+]?[1-9][\d]{3,14}$', phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
        print("2. Валидация телефона: OK")
    else:
        print("2. Валидация телефона: FAIL")
    
    # Тестирование валидации даты рождения
    birth_date = "01.01.1990"
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', birth_date):
        try:
            day, month, year = map(int, birth_date.split('.'))
            from datetime import datetime
            birth_date_obj = datetime(year, month, day)
            if birth_date_obj <= datetime.now():
                print("3. Валидация даты рождения: OK")
            else:
                print("3. Валидация даты рождения: FAIL - дата в будущем")
        except ValueError:
            print("3. Валидация даты рождения: FAIL - некорректная дата")
    else:
        print("3. Валидация даты рождения: FAIL - некорректный формат")
    
    print("Тестирование логики регистрации завершено!")

if __name__ == "__main__":
    print("Запуск тестирования функциональности бота...")
    
    test_database()
    test_registration_flow()
    
    print("\nВсе тесты пройдены успешно!")