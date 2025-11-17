import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создание таблицы пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создание таблицы мероприятий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TIMESTAMP,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создание таблицы регистрации на мероприятия
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (event_id) REFERENCES events (id),
                UNIQUE(user_id, event_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")
    
    def add_user(self, telegram_id: int, full_name: str, email: str, phone: str, birth_date: str):
        """Добавление нового пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, full_name, email, phone, birth_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, full_name, email, phone, birth_date))
            conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"Пользователь {full_name} добавлен с ID {user_id}")
            return user_id
        except sqlite3.IntegrityError:
            # Пользователь с таким telegram_id уже существует
            logger.warning(f"Пользователь с telegram_id {telegram_id} уже существует")
            return None
        finally:
            conn.close()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Получение информации о пользователе по telegram_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()
        
        if row:
            columns = ['id', 'telegram_id', 'full_name', 'email', 'phone', 'birth_date', 'registration_date']
            user = dict(zip(columns, row))
            conn.close()
            return user
        else:
            conn.close()
            return None
    
    def update_user(self, telegram_id: int, full_name: str, email: str, phone: str, birth_date: str):
        """Обновление информации о пользователе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET full_name = ?, email = ?, phone = ?, birth_date = ?
            WHERE telegram_id = ?
        ''', (full_name, email, phone, birth_date, telegram_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Информация о пользователе {telegram_id} обновлена")
    
    def add_event(self, title: str, description: str, date: str, location: str) -> int:
        """Добавление нового мероприятия"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (title, description, date, location)
            VALUES (?, ?, ?, ?)
        ''', (title, description, date, location))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Мероприятие '{title}' добавлено с ID {event_id}")
        return event_id
    
    def get_all_events(self) -> List[Dict]:
        """Получение всех мероприятий"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM events ORDER BY date')
        rows = cursor.fetchall()
        
        events = []
        if rows:
            columns = ['id', 'title', 'description', 'date', 'location', 'created_at']
            for row in rows:
                events.append(dict(zip(columns, row)))
        
        conn.close()
        return events
    
    def register_user_for_event(self, user_id: int, event_id: int):
        """Регистрация пользователя на мероприятие"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO event_registrations (user_id, event_id)
                VALUES (?, ?)
            ''', (user_id, event_id))
            conn.commit()
            logger.info(f"Пользователь {user_id} зарегистрирован на мероприятие {event_id}")
        except sqlite3.IntegrityError:
            # Пользователь уже зарегистрирован на это мероприятие
            logger.warning(f"Пользователь {user_id} уже зарегистрирован на мероприятие {event_id}")
        finally:
            conn.close()
    
    def get_user_registrations(self, user_id: int) -> List[Dict]:
        """Получение всех регистраций пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT e.id, e.title, e.description, e.date, e.location, er.registration_date
            FROM events e
            JOIN event_registrations er ON e.id = er.event_id
            WHERE er.user_id = ?
            ORDER BY e.date
        ''', (user_id,))
        
        rows = cursor.fetchall()
        registrations = []
        
        if rows:
            columns = ['event_id', 'title', 'description', 'date', 'location', 'registration_date']
            for row in rows:
                registrations.append(dict(zip(columns, row)))
        
        conn.close()
        return registrations
    
    def get_event_registrations(self, event_id: int) -> List[Dict]:
        """Получение всех регистраций на мероприятие"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.full_name, u.email, u.phone, u.birth_date, er.registration_date
            FROM users u
            JOIN event_registrations er ON u.id = er.user_id
            WHERE er.event_id = ?
            ORDER BY er.registration_date
        ''', (event_id,))
        
        rows = cursor.fetchall()
        registrations = []
        
        if rows:
            columns = ['full_name', 'email', 'phone', 'birth_date', 'registration_date']
            for row in rows:
                registrations.append(dict(zip(columns, row)))
        
        conn.close()
        return registrations
    
    def get_registration_stats(self) -> Dict:
        """Получение статистики регистрации"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общее количество пользователей
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Общее количество мероприятий
        cursor.execute('SELECT COUNT(*) FROM events')
        total_events = cursor.fetchone()[0]
        
        # Общее количество регистраций
        cursor.execute('SELECT COUNT(*) FROM event_registrations')
        total_registrations = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_events': total_events,
            'total_registrations': total_registrations
        }