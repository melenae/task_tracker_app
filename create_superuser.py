#!/usr/bin/env python
"""Скрипт для создания суперпользователя Django"""
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_track.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Данные для суперпользователя
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

# Проверяем, существует ли уже пользователь
if User.objects.filter(username=username).exists():
    print(f'Пользователь "{username}" уже существует!')
else:
    # Создаем суперпользователя
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'Суперпользователь "{username}" успешно создан!')
    print(f'Email: {email}')
    print(f'Пароль: {password}')

