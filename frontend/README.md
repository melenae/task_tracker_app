# Task Track Frontend

React frontend для Task Track приложения.

## Установка

```bash
npm install
```

## Запуск в режиме разработки

```bash
npm start
```

Приложение будет доступно по адресу: http://localhost:3000

## Сборка для production

```bash
npm run build
```

## API Endpoints

Frontend использует следующие API endpoints:

- `POST /api/login/` - Авторизация
- `POST /api/logout/` - Выход
- `GET /api/current-user/` - Текущий пользователь
- `GET /api/issues/` - Список задач
- `GET /api/projects/` - Список проектов
- `GET /api/users/` - Список пользователей
- И другие...

## Настройка

В `package.json` настроен proxy на `http://localhost:8000` для удобной работы с Django API в режиме разработки.

## Docker

Для запуска через Docker используйте:

```bash
docker-compose up frontend
```

Или запустите весь стек:

```bash
docker-compose up
```
