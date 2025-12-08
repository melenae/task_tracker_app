#!/usr/bin/env python
"""Скрипт для проверки данных в таблицах Users и Accounts"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_track.settings')
django.setup()

from erp_tools.models import Users, Accounts

print("=" * 50)
print("ПРОВЕРКА ТАБЛИЦЫ USERS")
print("=" * 50)
users = Users.objects.all()
print(f"Всего пользователей: {users.count()}\n")

for user in users:
    print(f"ID: {user.id}")
    print(f"  Phone: {user.phone}")
    print(f"  Role: {user.role}")
    print(f"  Bio: {user.bio}")
    print(f"  Owner (Account ID): {user.owner_id}")
    print(f"  Created: {user.created_at}")
    print(f"  Updated: {user.updated_at}")
    print("-" * 30)

print("\n" + "=" * 50)
print("ПРОВЕРКА ТАБЛИЦЫ ACCOUNTS")
print("=" * 50)
accounts = Accounts.objects.all()
print(f"Всего аккаунтов: {accounts.count()}\n")

for account in accounts:
    print(f"ID: {account.id}")
    print(f"  Slug: {account.slug}")
    print(f"  Content: {account.content}")
    print(f"  User (Manager ID): {account.user_id}")
    print(f"  Date Create: {account.date_create}")
    print(f"  Date Expired: {account.date_expired}")
    print("-" * 30)

