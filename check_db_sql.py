#!/usr/bin/env python
"""Проверка данных через прямой SQL запрос"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Настройка переменных окружения для decouple
from decouple import config, Csv
from decouple import Config, RepositoryEnv

# Ищем .env файл
env_file = BASE_DIR / '.env'
if env_file.exists():
    config = Config(RepositoryEnv(str(env_file)))

import psycopg2

try:
    conn = psycopg2.connect(
        dbname=config('DB_NAME', default='task_track'),
        user=config('DB_USER', default='postgres'),
        password=config('DB_PASSWORD', default=''),
        host=config('DB_HOST', default='localhost'),
        port=config('DB_PORT', default='5432')
    )
    cur = conn.cursor()
    
    print("=" * 60)
    print("ПРОВЕРКА ТАБЛИЦЫ erp_tools_users")
    print("=" * 60)
    cur.execute("SELECT * FROM erp_tools_users")
    columns = [desc[0] for desc in cur.description]
    print(f"Колонки: {', '.join(columns)}\n")
    
    rows = cur.fetchall()
    print(f"Всего записей: {len(rows)}\n")
    for row in rows:
        for i, col in enumerate(columns):
            print(f"  {col}: {row[i]}")
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ТАБЛИЦЫ erp_tools_accounts")
    print("=" * 60)
    cur.execute("SELECT * FROM erp_tools_accounts")
    columns = [desc[0] for desc in cur.description]
    print(f"Колонки: {', '.join(columns)}\n")
    
    rows = cur.fetchall()
    print(f"Всего записей: {len(rows)}\n")
    for row in rows:
        for i, col in enumerate(columns):
            print(f"  {col}: {row[i]}")
        print("-" * 40)
    
    conn.close()
    
except Exception as e:
    print(f"Ошибка: {e}")

