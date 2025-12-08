<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Track - Issue Tracking System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 50px;
            animation: fadeInDown 0.8s ease;
        }

        .header h1 {
            font-size: 3.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.3em;
            opacity: 0.9;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: fadeInUp 0.8s ease;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }

        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        .card h3 {
            color: #764ba2;
            margin: 20px 0 10px 0;
            font-size: 1.4em;
        }

        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }

        .tech-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .feature-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }

        .feature-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }

        .feature-item h4 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .kafka-flow {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 15px;
            text-align: center;
        }

        .flow-arrow {
            font-size: 2em;
            color: #667eea;
            margin: 10px 0;
        }

        .flow-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .github-link {
            display: inline-block;
            background: #24292e;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }

        .github-link:hover {
            background: #2f363d;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .highlight {
            background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }

        ul {
            list-style: none;
            padding-left: 0;
        }

        ul li {
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }

        ul li:before {
            content: "▸";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Task Track</h1>
            <p>Issue Tracking System with Kafka Integration</p>
        </div>

        <div class="card">
            <h2>📋 О проекте</h2>
            <p>
                <strong>Task Track</strong> — веб-приложение для расширения функциональности десктопного приложения 
                <span class="highlight">ERP-tools</span> — профессионального инструмента для командной работы над внедрением ERP систем.
            </p>
            <p style="margin-top: 15px;">
                Проект обеспечивает возможность работы с таск-трекером через веб-интерфейс с двусторонней синхронизацией 
                данных через Apache Kafka.
            </p>
        </div>

        <div class="card">
            <h2>🛠 Технологический стек</h2>
            <div class="tech-stack">
                <span class="tech-badge">Django 5.2</span>
                <span class="tech-badge">Python 3.12</span>
                <span class="tech-badge">PostgreSQL</span>
                <span class="tech-badge">Redis</span>
                <span class="tech-badge">Apache Kafka 7.5</span>
                <span class="tech-badge">Zookeeper</span>
                <span class="tech-badge">Docker Compose</span>
                <span class="tech-badge">Kafka UI</span>
            </div>
        </div>

        <div class="card">
            <h2>✨ Основной функционал</h2>
            <div class="features-grid">
                <div class="feature-item">
                    <h4>📝 Управление заявками</h4>
                    <p>Создание, обновление, смена статусов, комментарии к заявкам</p>
                </div>
                <div class="feature-item">
                    <h4>👥 Управление проектами</h4>
                    <p>Проекты, команды, роли участников, управление доступом</p>
                </div>
                <div class="feature-item">
                    <h4>🏢 Управление компаниями</h4>
                    <p>Компании, базы данных, сервисы, клиентские команды</p>
                </div>
                <div class="feature-item">
                    <h4>🔐 Система авторизации</h4>
                    <p>Email-логин, интеграция с Django Auth, управление правами</p>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔄 Интеграция с Kafka</h2>
            <div class="kafka-flow">
                <div class="flow-item">
                    <strong>Producer</strong><br>
                    Отправка событий о заявках (created, updated, deleted, status_changed, comment_added)
                </div>
                <div class="flow-arrow">⬇️</div>
                <div class="flow-item">
                    <strong>Kafka Topics</strong><br>
                    issues-events | issues-events-1c
                </div>
                <div class="flow-arrow">⬇️</div>
                <div class="flow-item">
                    <strong>Consumer</strong><br>
                    Получение событий от внешней системы (1С), синхронизация данных
                </div>
            </div>
            <ul style="margin-top: 20px;">
                <li>Consumer group: <code>django-task-track</code></li>
                <li>Асинхронная обработка сообщений в отдельном потоке</li>
                <li>Защита от зацикливания (игнорирование собственных событий)</li>
                <li>Автоматическая отправка событий через Django signals</li>
            </ul>
        </div>

        <div class="card">
            <h2>🏗 Архитектурные решения</h2>
            <ul>
                <li><strong>Event-driven архитектура</strong> через Kafka для асинхронной обработки событий</li>
                <li><strong>Микросервисная архитектура</strong> с поддержкой высокой нагрузки на БД</li>
                <li><strong>Docker Compose</strong> для оркестрации всех сервисов</li>
                <li><strong>Generic Foreign Keys</strong> для гибких связей между моделями</li>
                <li><strong>Система прав доступа</strong> через permitted_accounts</li>
                <li><strong>Логирование</strong> всех операций с Kafka для отладки</li>
            </ul>
        </div>

        <div class="card">
            <h2>🚀 DevOps</h2>
            <ul>
                <li>Docker Compose для развертывания (Kafka, Zookeeper, Kafka UI)</li>
                <li>Изоляция зависимостей через venv</li>
                <li>Конфигурация через переменные окружения (python-decouple)</li>
                <li>Автоматическое создание топиков Kafka</li>
                <li>Django Debug Toolbar для отладки</li>
            </ul>
        </div>

        <div class="card">
            <h2>📊 Объем проекта</h2>
            <ul>
                <li>18 миграций базы данных</li>
                <li>Множество моделей (Users, Projects, Issues, Companies, Services и др.)</li>
                <li>RESTful-подобные URL-маршруты</li>
                <li>HTML-шаблоны для всех сущностей</li>
                <li>Система форм для создания и редактирования</li>
            </ul>
        </div>

        <div class="card" style="text-align: center;">
            <h2>🔗 Ссылки</h2>
            <a href="https://github.com/melenae/task_tracker_app" class="github-link" target="_blank">
                📦 GitHub Repository
            </a>
        </div>
    </div>
</body>
</html>
