from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import re
from database import Database
from constants import *
from config import ADMIN_IDS

class RegistrationHandler:
    def __init__(self, db: Database):
        self.db = db
    
    def format_birth_date_display(self, birth_date_str):
        """
        Форматирует дату рождения для отображения
        Входной формат: ДД.ММ.ГГГГ
        Выходной формат: ДД Месяц ГГГГ (например, 12 Июнь 1995)
        """
        months = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        
        try:
            day, month, year = map(int, birth_date_str.split('.'))
            month_name = months[month]
            return f"{day} {month_name} {year}"
        except (ValueError, IndexError):
            # Если формат даты некорректен, возвращаем исходное значение
            return birth_date_str
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        keyboard = [
            ['/register', '/my_info'],
            ['/help']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        await update.message.reply_text(HELP_MESSAGE)
    
    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало процесса регистрации"""
        user = self.db.get_user_by_telegram_id(update.effective_user.id)
        if user:
            await update.message.reply_text(
                "Вы уже зарегистрированы. Если хотите обновить информацию, напишите об этом администратору."
            )
            return ConversationHandler.END
        
        await update.message.reply_text(
            NAME_REQUEST,
            reply_markup=ReplyKeyboardMarkup(
                [[CANCEL_BUTTON]], resize_keyboard=True
            )
        )
        return NAME
    
    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение имени пользователя"""
        if update.message.text == CANCEL_BUTTON:
            await update.message.reply_text(
                "Регистрация отменена.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        context.user_data['full_name'] = update.message.text
        await update.message.reply_text(
            EMAIL_REQUEST,
            reply_markup=ReplyKeyboardMarkup(
                [[CANCEL_BUTTON]], resize_keyboard=True
            )
        )
        return EMAIL
    
    async def get_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение email пользователя"""
        if update.message.text == CANCEL_BUTTON:
            await update.message.reply_text(
                "Регистрация отменена.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        email = update.message.text
        # Проверка формата email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await update.message.reply_text(INVALID_EMAIL)
            return EMAIL
        
        context.user_data['email'] = email
        await update.message.reply_text(
            PHONE_REQUEST,
            reply_markup=ReplyKeyboardMarkup(
                [[CANCEL_BUTTON]], resize_keyboard=True
            )
        )
        return PHONE
    
    async def get_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение номера телефона пользователя"""
        if update.message.text == CANCEL_BUTTON:
            await update.message.reply_text(
                "Регистрация отменена.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        phone = update.message.text
        # Проверка формата номера телефона (упрощенная)
        if not re.match(r'^[\+]?[1-9][\d]{3,14}$', phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            await update.message.reply_text(INVALID_PHONE)
            return PHONE
        
        context.user_data['phone'] = phone
        await update.message.reply_text(
            BIRTH_DATE_REQUEST,
            reply_markup=ReplyKeyboardMarkup(
                [[CANCEL_BUTTON]], resize_keyboard=True
            )
        )
        return BIRTH_DATE
    
    async def get_birth_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение даты рождения пользователя"""
        if update.message.text == CANCEL_BUTTON:
            await update.message.reply_text(
                "Регистрация отменена.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        birth_date = update.message.text
        # Проверка формата даты рождения (ДД.ММ.ГГГГ)
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birth_date):
            await update.message.reply_text(INVALID_DATE)
            return BIRTH_DATE
        
        # Проверка корректности даты
        try:
            day, month, year = map(int, birth_date.split('.'))
            from datetime import datetime
            birth_date_obj = datetime(year, month, day)
            if birth_date_obj > datetime.now():
                await update.message.reply_text(INVALID_DATE + " Дата не может быть в будущем.")
                return BIRTH_DATE
        except ValueError:
            await update.message.reply_text(INVALID_DATE)
            return BIRTH_DATE
        
        context.user_data['birth_date'] = birth_date
        
        # Показываем пользователю его данные для подтверждения
        # Форматируем дату рождения для отображения
        birth_date_display = self.format_birth_date_display(context.user_data['birth_date'])
        
        await update.message.reply_text(
            f"Пожалуйста, подтвердите ваши данные:\n\n"
            f"Имя: {context.user_data['full_name']}\n"
            f"Email: {context.user_data['email']}\n"
            f"Телефон: {context.user_data['phone']}\n"
            f"Дата рождения: {birth_date_display}\n\n"
            f"Нажмите '{CONFIRM_BUTTON}' для подтверждения или '{CANCEL_BUTTON}' для отмены.",
            reply_markup=ReplyKeyboardMarkup(
                [[CONFIRM_BUTTON, CANCEL_BUTTON]], resize_keyboard=True
            )
        )
        return CONFIRM
    
    async def confirm_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение регистрации"""
        # Проверяем, содержит ли сообщение текст подтверждения или отмены
        user_text = update.message.text.strip()
        
        if CONFIRM_BUTTON in user_text or 'Подтвердить' in user_text or 'подтвердить' in user_text:
            # Сохраняем пользователя в базу данных
            user_id = self.db.add_user(
                telegram_id=update.effective_user.id,
                full_name=context.user_data['full_name'],
                email=context.user_data['email'],
                phone=context.user_data['phone'],
                birth_date=context.user_data['birth_date']
            )
            
            if user_id:
                await update.message.reply_text(
                    REGISTRATION_SUCCESS,
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                await update.message.reply_text(
                    "Произошла ошибка при регистрации. Возможно, вы уже зарегистрированы.",
                    reply_markup=ReplyKeyboardRemove()
                )
        elif CANCEL_BUTTON in user_text or 'Отмена' in user_text or 'отмена' in user_text:
            await update.message.reply_text(
                "Регистрация отменена.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            # Если пользователь ввел что-то другое, переспрашиваем
            await update.message.reply_text(
                f"Пожалуйста, нажмите '{CONFIRM_BUTTON}' для подтверждения или '{CANCEL_BUTTON}' для отмены.",
                reply_markup=ReplyKeyboardMarkup(
                    [[CONFIRM_BUTTON, CANCEL_BUTTON]], resize_keyboard=True
                )
            )
            return CONFIRM
        
        # Очищаем данные пользователя
        context.user_data.clear()
        return ConversationHandler.END
    
    async def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена регистрации"""
        await update.message.reply_text(
            "Регистрация отменена.",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    async def my_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать информацию о пользователе"""
        user = self.db.get_user_by_telegram_id(update.effective_user.id)
        if user:
            # Форматируем дату рождения для отображения
            birth_date_display = self.format_birth_date_display(user['birth_date'])
            
            await update.message.reply_text(
                f"Ваша информация:\n\n"
                f"Имя: {user['full_name']}\n"
                f"Email: {user['email']}\n"
                f"Телефон: {user['phone']}\n"
                f"Дата рождения: {birth_date_display}\n"
                f"Дата регистрации: {user['registration_date']}"
            )
        else:
            await update.message.reply_text(
                "Вы не зарегистрированы. Используйте команду /register для регистрации."
            )
    
    # Функции для админ-панели
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для администратора"""
        # Проверяем, является ли пользователь администратором
        if str(update.effective_user.id) not in ADMIN_IDS:
            await update.message.reply_text("У вас нет прав администратора.")
            return
        
        keyboard = [
            ['/stats', '/new_event'],
            ['/events_list']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            ADMIN_MENU_MESSAGE,
            reply_markup=reply_markup
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать статистику регистрации"""
        # Проверяем, является ли пользователь администратором
        if str(update.effective_user.id) not in ADMIN_IDS:
            await update.message.reply_text("У вас нет прав администратора.")
            return
        
        stats = self.db.get_registration_stats()
        
        await update.message.reply_text(
            f"{ADMIN_STATS_MESSAGE}\n\n"
            f"Всего пользователей: {stats['total_users']}\n"
            f"Всего мероприятий: {stats['total_events']}\n"
            f"Всего регистраций: {stats['total_registrations']}"
        )
    
    async def new_event_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать создание нового мероприятия (заглушка)"""
        # Проверяем, является ли пользователь администратором
        if str(update.effective_user.id) not in ADMIN_IDS:
            await update.message.reply_text("У вас нет прав администратора.")
            return
        
        await update.message.reply_text("Функция создания нового мероприятия в разработке.")