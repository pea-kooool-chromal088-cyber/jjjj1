#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для перезапуска бота с новыми настройками администратора
"""

import subprocess
import sys
import os
import signal
import time

def stop_running_bots():
    """Останавливает все запущенные экземпляры бота"""
    print("Остановка запущенных экземпляров бота...")
    
    # Пытаемся найти и завершить процессы Python, запускающие бота
    try:
        # В Windows используем taskkill для завершения процессов python с bot.py
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and 'bot.py' in ' '.join(proc.info['cmdline'] or []).lower():
                    print(f"Завершение процесса {proc.info['pid']}: {' '.join(proc.info['cmdline'] or [])}")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except ImportError:
        # Если psutil не установлен, используем taskkill
        try:
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
        except Exception:
            print("Не удалось завершить процессы через taskkill")
    
    print("Ожидание завершения процессов...")
    time.sleep(2)

def start_bot():
    """Запускает бота в новом процессе"""
    print("Запуск бота с новыми настройками администратора...")
    
    try:
        # Запускаем бота в фоновом режиме
        process = subprocess.Popen([sys.executable, 'bot.py'])
        print(f"Бот запущен с PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        return None

def main():
    print("Перезапуск Telegram-бота...")
    print("Текущий каталог:", os.getcwd())
    
    # Останавливаем запущенные экземпляры
    stop_running_bots()
    
    # Ждем немного перед перезапуском
    time.sleep(3)
    
    # Запускаем бота с новыми настройками
    bot_process = start_bot()
    
    if bot_process:
        print("Бот успешно перезапущен с новыми настройками администратора.")
        print("Пользователь с ID 7153370696 теперь имеет права администратора.")
        print("\nДоступные команды администратора:")
        print("/admin - открыть админ-панель")
        print("/stats - посмотреть статистику регистрации")
        print("/new_event - создать новое мероприятие")
    else:
        print("Не удалось перезапустить бота.")

if __name__ == "__main__":
    main()