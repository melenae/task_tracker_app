# Настройка React Frontend для Task Track

## ✅ Что было сделано:

1. ✅ Создана папка `frontend/` с React приложением
2. ✅ Обновлен `.gitignore` для исключения React файлов
3. ✅ Добавлены зависимости в `requirements.txt`:
   - `django-cors-headers` - для CORS
   - `djangorestframework` - для REST API
4. ✅ Настроен CORS в `task_track/settings.py`
5. ✅ Созданы API endpoints:
   - `erp_tools/api_views.py` - API views
   - `erp_tools/serializers.py` - сериализаторы
   - Обновлен `task_track/urls.py` с API роутами
6. ✅ Обновлен `docker-compose.yml` для React dev server
7. ✅ Создан базовый React компонент с примером работы с API

## 🚀 Запуск проекта

### Вариант 1: Локальный запуск (без Docker)

1. **Установите зависимости Django:**
```bash
pip install -r requirements.txt
```

2. **Запустите Django сервер:**
```bash
python manage.py runserver
```

3. **В другом терминале запустите React:**
```bash
cd frontend
npm install
npm start
```

React будет доступен на http://localhost:3000
Django API на http://localhost:8000

### Вариант 2: Запуск через Docker

```bash
docker-compose up
```

## 📡 API Endpoints

Все API endpoints доступны по префиксу `/api/`:

- `POST /api/login/` - Авторизация
- `POST /api/logout/` - Выход
- `GET /api/current-user/` - Текущий пользователь
- `GET /api/issues/` - Список задач
- `GET /api/projects/` - Список проектов
- `GET /api/users/` - Список пользователей
- `GET /api/accounts/` - Список аккаунтов
- `GET /api/companies/` - Список компаний
- `GET /api/databases/` - Список баз данных
- `GET /api/services/` - Список услуг
- `GET /api/project-teams/` - Команды проектов
- `GET /api/client-teams/` - Команды клиентов
- `GET /api/comments/` - Комментарии к задачам

Все endpoints поддерживают стандартные CRUD операции через ViewSets.

## 🔧 Настройки

### CORS
Настроен для работы с React dev server на `localhost:3000`

### Proxy
В `frontend/package.json` настроен proxy на `http://localhost:8000` для удобной работы в режиме разработки.

## 📝 Следующие шаги

1. Расширить React компоненты для всех сущностей
2. Добавить роутинг (React Router)
3. Добавить состояние (Redux/Context API)
4. Улучшить UI/UX
5. Добавить обработку ошибок
6. Настроить production сборку

## 🐛 Отладка

Если возникают проблемы с CORS:
- Проверьте, что `corsheaders` добавлен в `INSTALLED_APPS`
- Проверьте, что `CorsMiddleware` добавлен в `MIDDLEWARE`
- Проверьте настройки `CORS_ALLOWED_ORIGINS` в `settings.py`





