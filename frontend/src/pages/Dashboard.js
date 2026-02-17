import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getData();
      setData(response.data);
      setError(null);
    } catch (err) {
      setError('Ошибка загрузки данных. Проверьте подключение к серверу.');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusLabel = (status) => {
    const statusMap = {
      'new': 'Новая',
      'in_progress': 'В работе',
      'waiting': 'Ожидает',
      'testing': 'Тестирование',
      'done': 'Выполнена',
      'closed': 'Закрыта',
    };
    return statusMap[status] || status;
  };

  const getStatusClass = (status) => {
    const classMap = {
      'new': 'status-new',
      'in_progress': 'status-in-progress',
      'waiting': 'status-waiting',
      'testing': 'status-testing',
      'done': 'status-done',
      'closed': 'status-closed',
    };
    return classMap[status] || '';
  };

  const getPriorityLabel = (priority) => {
    const priorityMap = {
      'low': 'Низкий',
      'medium': 'Средний',
      'high': 'Высокий',
    };
    return priorityMap[priority] || priority;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} мин назад`;
    } else if (diffHours < 24) {
      return `${diffHours} ч назад`;
    } else if (diffDays < 7) {
      return `${diffDays} дн назад`;
    } else {
      return date.toLocaleDateString('ru-RU');
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Загрузка данных...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>{error}</p>
        <button onClick={loadDashboardData} className="retry-btn">
          Повторить
        </button>
      </div>
    );
  }

  if (!data) {
    return <div className="dashboard-error">Нет данных для отображения</div>;
  }

  return (
    <div className="dashboard">
      {/* Заголовок */}
      <div className="dashboard-header">
        <h1>Добро пожаловать, {user?.name || user?.email || 'Пользователь'}!</h1>
        <p className="dashboard-date">{new Date().toLocaleDateString('ru-RU', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>

      {/* Статистические карточки */}
      <div className="stats-grid">
        <div className="stat-card stat-total">
          <div className="stat-content">
            <div className="stat-value">{data.stats?.total || 0}</div>
            <div className="stat-label">Всего задач</div>
          </div>
        </div>
        <div className="stat-card stat-done">
          <div className="stat-content">
            <div className="stat-value">{data.stats?.done || 0}</div>
            <div className="stat-label">Выполнено</div>
          </div>
        </div>
        <div className="stat-card stat-progress">
          <div className="stat-content">
            <div className="stat-value">{data.stats?.in_progress || 0}</div>
            <div className="stat-label">В работе</div>
          </div>
        </div>
        <div className="stat-card stat-overdue">
          <div className="stat-content">
            <div className="stat-value">{data.stats?.overdue || 0}</div>
            <div className="stat-label">Просрочено</div>
          </div>
        </div>
      </div>

      {/* Основной контент - две колонки */}
      <div className="dashboard-content">
        {/* Левая колонка */}
        <div className="dashboard-column">
          {/* Мои задачи */}
          <div className="dashboard-section">
            <div className="section-header">
              <h2>Мои задачи</h2>
              <Link to="/issues" className="section-link">
                Показать все →
              </Link>
            </div>
            <div className="section-content">
              {data.my_issues && data.my_issues.length > 0 ? (
                <ul className="issue-list">
                  {data.my_issues.map((issue) => (
                    <li key={issue.id} className="issue-item">
                      <Link to={`/issues/${issue.id}`} className="issue-link">
                        <div className="issue-header">
                          <span className="issue-title">{issue.name}</span>
                          <span className={`issue-status ${getStatusClass(issue.status)}`}>
                            {getStatusLabel(issue.status)}
                          </span>
                        </div>
                        {issue.companies_name && (
                          <div className="issue-meta">
                            <span className="issue-project">{issue.companies_name}</span>
                          </div>
                        )}
                        {issue.priority && (
                          <div className="issue-priority">
                            Приоритет: {getPriorityLabel(issue.priority)}
                          </div>
                        )}
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-state">Нет назначенных задач</p>
              )}
            </div>
          </div>

          {/* Активные проекты */}
          <div className="dashboard-section">
            <div className="section-header">
              <h2>Активные проекты</h2>
              <Link to="/projects" className="section-link">
                Показать все →
              </Link>
            </div>
            <div className="section-content">
              {data.active_projects && data.active_projects.length > 0 ? (
                <ul className="project-list">
                  {data.active_projects.map((project) => (
                    <li key={project.id} className="project-item">
                      <Link to={`/projects/${project.id}`} className="project-link">
                        <div className="project-header">
                          <span className="project-title">{project.name}</span>
                        </div>
                        <div className="project-progress">
                          <div className="progress-bar">
                            <div
                              className="progress-fill"
                              style={{ width: `${project.progress || 0}%` }}
                            ></div>
                          </div>
                          <div className="progress-text">
                            {project.done_issues || 0} / {project.total_issues || 0} задач
                          </div>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-state">Нет активных проектов</p>
              )}
            </div>
          </div>
        </div>

        {/* Правая колонка */}
        <div className="dashboard-column">
          {/* Быстрые действия */}
          <div className="dashboard-section">
            <div className="section-header">
              <h2>Быстрые действия</h2>
            </div>
            <div className="section-content">
              <div className="quick-actions">
                <Link to="/issues/create" className="quick-action-btn primary">
                  Создать задачу
                </Link>
                <Link to="/projects" className="quick-action-btn">
                  Создать проект
                </Link>
                <Link to="/issues" className="quick-action-btn">
                  Все задачи
                </Link>
                <Link to="/projects" className="quick-action-btn">
                  Все проекты
                </Link>
                <Link to="/users" className="quick-action-btn">
                  Команда
                </Link>
                <Link to="/companies" className="quick-action-btn">
                  Компании
                </Link>
              </div>
            </div>
          </div>

          {/* Недавние задачи */}
          <div className="dashboard-section">
            <div className="section-header">
              <h2>Недавние задачи</h2>
              <Link to="/issues" className="section-link">
                Показать все →
              </Link>
            </div>
            <div className="section-content">
              {data.recent_issues && data.recent_issues.length > 0 ? (
                <ul className="issue-list">
                  {data.recent_issues.map((issue) => (
                    <li key={issue.id} className="issue-item">
                      <Link to={`/issues/${issue.id}`} className="issue-link">
                        <div className="issue-header">
                          <span className="issue-title">{issue.name}</span>
                          <span className={`issue-status ${getStatusClass(issue.status)}`}>
                            {getStatusLabel(issue.status)}
                          </span>
                        </div>
                        {issue.companies_name && (
                          <div className="issue-meta">
                            <span className="issue-project">{issue.companies_name}</span>
                          </div>
                        )}
                        <div className="issue-time">
                          {formatDate(issue.date_create)}
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-state">Нет недавних задач</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

