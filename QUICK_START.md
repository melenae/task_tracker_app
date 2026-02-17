# Быстрый старт

## Рекомендуемый способ (локальный запуск)

### 1. Запустите Kafka сервисы через Docker:
```bash
docker-compose up -d zookeeper kafka kafka-ui
```

### 2. Запустите Django сервер:
```bash
python manage.py runserver
```

### 3. В другом терминале запустите React:
```bash
cd frontend
npm install  # только при первом запуске
npm start
```

**Преимущества:**
- ✅ Быстрый запуск
- ✅ Горячая перезагрузка работает мгновенно
- ✅ Не нужно ждать сборки Docker образа
- ✅ Меньше нагрузка на систему

## Альтернатива: Запуск через Docker (медленнее)

Если все же хотите использовать Docker для frontend:

1. Раскомментируйте секцию `frontend` в `docker-compose.yml`
2. Запустите:
```bash
docker-compose up frontend
```

**Недостатки:**
- ⚠️ Долгая первая сборка (копирование node_modules)
- ⚠️ Медленнее горячая перезагрузка
- ⚠️ Больше потребление ресурсов

## Порты

- Django API: http://localhost:8000
- React App: http://localhost:3000
- Kafka UI: http://localhost:8081





