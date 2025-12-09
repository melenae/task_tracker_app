# 🚀 Task Track

**Issue Tracking System with Kafka Integration**

Web application for extending the functionality of the desktop application **ERP-tools** — a professional tool for team collaboration on ERP system implementation.

---

## 📋 About the Project

Task Track enables web-based task tracking with bidirectional data synchronization through Apache Kafka.

## 🛠 Technology Stack

![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

- **Backend:** Django 5.2, Python 3.12
- **Database:** PostgreSQL (psycopg2-binary)
- **Caching:** Redis (django-redis)
- **Messaging:** Apache Kafka 7.5, Zookeeper
- **Monitoring:** Kafka UI
- **Infrastructure:** Docker Compose
- **Configuration:** python-decouple

## ✨ Core Features

### 📝 Issue Management
- Create, update, delete issues
- Status changes
- Comments on issues
- Filtering by projects and statuses

### 👥 Project Management
- Create and manage projects
- Project teams with participant roles
- Access control via permitted_accounts

### 🏢 Company & Client Management
- Companies and databases
- Services and client teams
- Relationships between entities

### 🔐 Authentication System
- Email login
- Django Auth integration
- Access rights management

### Producer
Sending issue events:
- `created` - issue creation
- `updated` - issue update
- `deleted` - issue deletion
- `status_changed` - status change
- `comment_added` - comment addition

### Consumer
- Receiving events from external system (1C)
- Data synchronization
- Consumer group: `django-task-track`
- Topics: `issues-events`, `issues-events-1c`

### Features
- ✅ Asynchronous message processing in separate thread
- ✅ Loop prevention (ignoring own events)
- ✅ Automatic event publishing via Django signals
- ✅ Logging of all Kafka operations

## 🏗 Architectural Solutions

- **Event-driven architecture** via Kafka for asynchronous event processing
- **Microservices architecture** with support for high database load
- **Docker Compose** for service orchestration
- **Generic Foreign Keys** for flexible model relationships
- **Access control system** via permitted_accounts
- **Logging** of all Kafka operations for debugging

## 🚀 Quick Start

### Requirements
- Python 3.12+
- Docker and Docker Compose
- PostgreSQL

### Installation

1. **Clone the repository**
git clone https://github.com/melenae/task_tracker_app.git
cd task_tracker_app2. **Create virtual environment**
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate3. **Install dependencies**
pip install -r requirements.txt4. **Configure environment variables**
Create `.env` file:
DB_NAME=task_track
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
KAFKA_BOOTSTRAP_SERVERS=localhost:90925. **Start Docker containers**
docker-compose up -d6. **Run migrations**
python manage.py migrate7. **Create superuser**sh
python manage.py createsuperuser8. **Run development server**
python manage.py runserver## 📊 Project Scope

- 18 database migrations
- Multiple models (Users, Projects, Issues, Companies, Services, etc.)
- RESTful-like URL routing
- HTML templates for all entities
- Form system for creation and editing

## 🛠 Development Tools

- **Cursor AI** - for accelerated development and refactoring
- **Django Debug Toolbar** - for debugging
- **python-decouple** - for environment variable management

## 📝 Project Structure
