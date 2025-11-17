#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для заполнения базы данных случайными данными
"""

import random
from database import Database

def generate_random_data():
    """Генерация случайных данных для тестирования"""
    first_names = ["Иван", "Петр", "Сидор", "Алексей", "Михаил", "Дмитрий", "Андрей", "Сергей", "Владимир", "Александр"]
    last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Волков", "Зайцев", "Васильев", "Морозов", "Новиков"]
    domains = ["gmail.com", "yandex.ru", "mail.ru", "outlook.com", "hotmail.com"]
    
    users = []
    for i in range(20):  # Создаем 20 случайных пользователей
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"
        phone = f"+7{random.randint(100000, 999999)}"
        birth_date = f"{random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(1970, 2000)}"
        
        users.append({
            'telegram_id': 10000000 + i,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'birth_date': birth_date
        })
    
    return users

def main():
    # Инициализация базы данных
    db = Database("registrations.db")
    
    # Генерация случайных данных
    users = generate_random_data()
    
    # Добавление пользователей в базу данных
    for user in users:
        user_id = db.add_user(
            telegram_id=user['telegram_id'],
            full_name=user['full_name'],
            email=user['email'],
            phone=user['phone'],
            birth_date=user['birth_date']
        )
        if user_id:
            print(f"Добавлен пользователь: {user['full_name']}, ID: {user_id}")
        else:
            print(f"Ошибка при добавлении пользователя: {user['full_name']}")
    
    # Создание нескольких тестовых мероприятий
    events = [
        {
            'title': 'Конференция разработчиков',
            'description': 'Ежегодная конференция для разработчиков',
            'date': '2024-12-15 10:00:00',
            'location': 'Москва, Красная площадь, 1'
        },
        {
            'title': 'Мастер-класс по Python',
            'description': 'Практический мастер-класс по Python',
            'date': '2024-12-20 14:00:00',
            'location': 'Онлайн'
        },
        {
            'title': 'Встреча фрилансеров',
            'description': 'Неформальная встреча фрилансеров',
            'date': '2024-12-25 18:00:00',
            'location': 'Кафе "Уголок", Невский проспект, 50'
        }
    ]
    
    for event in events:
        event_id = db.add_event(
            title=event['title'],
            description=event['description'],
            date=event['date'],
            location=event['location']
        )
        if event_id:
            print(f"Добавлено мероприятие: {event['title']}, ID: {event_id}")
        else:
            print(f"Ошибка при добавлении мероприятия: {event['title']}")
    
    # Случайным образом регистрируем пользователей на мероприятия
    all_events = db.get_all_events()
    for user in users:
        user_db = db.get_user_by_telegram_id(user['telegram_id'])
        if user_db:
            # Регистрируем пользователя на 0-2 случайных мероприятиях
            num_events = random.randint(0, 2)
            selected_events = random.sample(all_events, min(num_events, len(all_events)))
            
            for event in selected_events:
                db.register_user_for_event(user_db['id'], event['id'])
                print(f"Пользователь {user_db['full_name']} зарегистрирован на мероприятие '{event['title']}'")
    
    print("\nБаза данных успешно заполнена случайными данными!")
    
    # Выводим статистику
    stats = db.get_registration_stats()
    print(f"\nТекущая статистика:")
    print(f"Пользователей: {stats['total_users']}")
    print(f"Мероприятий: {stats['total_events']}")
    print(f"Регистраций: {stats['total_registrations']}")

if __name__ == "__main__":
    main()