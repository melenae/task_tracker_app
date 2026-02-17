import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { issuesAPI, projectsAPI } from '../services/api';
import './IssuesList.css';

const IssuesList = () => {
  const [issues, setIssues] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [viewMode, setViewMode] = useState('table');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [selectedProject]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [issuesRes, projectsRes] = await Promise.all([
        issuesAPI.list({ project: selectedProject || undefined }),
        projectsAPI.list(),
      ]);
      
      // Обрабатываем ответы
      const issuesData = issuesRes.data?.results || issuesRes.data || [];
      const projectsData = projectsRes.data?.results || projectsRes.data || [];
      
      setIssues(Array.isArray(issuesData) ? issuesData : []);
      setProjects(Array.isArray(projectsData) ? projectsData : []);
    } catch (err) {
      console.error('Ошибка загрузки:', err);
      console.error('Response:', err.response);
      
      if (err.response?.status === 403) {
        setError('Недостаточно прав для просмотра данных');
      } else if (err.response?.status === 404) {
        setError('API endpoint не найден. Проверьте настройки сервера.');
      } else if (err.response?.data?.error) {
        setError(`Ошибка: ${err.response.data.error}`);
      } else {
        setError(`Ошибка загрузки данных: ${err.message || 'Проверьте подключение к серверу'}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      new: 'Новая',
      in_progress: 'В работе',
      waiting: 'Ожидает',
      testing: 'Тестирование',
      done: 'Выполнена',
      closed: 'Закрыта',
    };
    return labels[status] || status;
  };

  const getStatusClass = (status) => {
    return `status status-${status}`;
  };

  const getPriorityLabel = (priority) => {
    const labels = {
      low: 'Низкий',
      medium: 'Средний',
      high: 'Высокий',
    };
    return labels[priority] || priority;
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="issues-list">
      <div className="page-header">
        <h1>Задачи</h1>
        <Link to="/issues/create" className="btn btn-primary">
          Создать задачу
        </Link>
      </div>

      <div className="filters">
        <div className="filter-group">
          <label>Проект:</label>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
          >
            <option value="">Все проекты</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
        <div className="view-toggle">
          <button
            className={viewMode === 'table' ? 'active' : ''}
            onClick={() => setViewMode('table')}
          >
            Таблица
          </button>
          <button
            className={viewMode === 'kanban' ? 'active' : ''}
            onClick={() => setViewMode('kanban')}
          >
            Канбан
          </button>
        </div>
      </div>

      {viewMode === 'table' ? (
        <table className="issues-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Статус</th>
              <th>Приоритет</th>
              <th>Дата создания</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {issues.length === 0 ? (
              <tr>
                <td colSpan="6" className="empty">Нет задач</td>
              </tr>
            ) : (
              issues.map((issue) => (
                <tr key={issue.id}>
                  <td>#{issue.id}</td>
                  <td>
                    <Link to={`/issues/${issue.id}`}>{issue.name}</Link>
                  </td>
                  <td>
                    <span className={getStatusClass(issue.status)}>
                      {getStatusLabel(issue.status)}
                    </span>
                  </td>
                  <td>{getPriorityLabel(issue.priority)}</td>
                  <td>
                    {new Date(issue.date_create).toLocaleDateString('ru-RU')}
                  </td>
                  <td>
                    <Link to={`/issues/${issue.id}`} className="btn btn-sm">
                      Открыть
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      ) : (
        <KanbanBoard issues={issues} onUpdate={loadData} />
      )}
    </div>
  );
};

const KanbanBoard = ({ issues, onUpdate }) => {
  const statuses = [
    { code: 'new', label: 'Новая' },
    { code: 'in_progress', label: 'В работе' },
    { code: 'waiting', label: 'Ожидает' },
    { code: 'testing', label: 'Тестирование' },
    { code: 'done', label: 'Выполнена' },
    { code: 'closed', label: 'Закрыта' },
  ];

  const handleStatusChange = async (issueId, newStatus) => {
    try {
      await issuesAPI.updateStatus(issueId, newStatus);
      onUpdate();
    } catch (error) {
      console.error('Ошибка обновления статуса:', error);
      alert('Не удалось изменить статус');
    }
  };

  return (
    <div className="kanban-board">
      {statuses.map((status) => {
        const statusIssues = issues.filter((issue) => issue.status === status.code);
        return (
          <div key={status.code} className="kanban-column">
            <div className="kanban-column-header">
              <h3>{status.label}</h3>
              <span className="badge">{statusIssues.length}</span>
            </div>
            <div className="kanban-column-content">
              {statusIssues.map((issue) => (
                <div key={issue.id} className="kanban-card">
                  <Link to={`/issues/${issue.id}`}>
                    <h4>{issue.name}</h4>
                    {issue.content && (
                      <p className="kanban-card-content">
                        {issue.content.substring(0, 100)}
                        {issue.content.length > 100 && '...'}
                      </p>
                    )}
                  </Link>
                  <div className="kanban-card-footer">
                    <span className={`priority-badge priority-${issue.priority}`}>
                      {issue.priority}
                    </span>
                    <select
                      value={issue.status}
                      onChange={(e) => handleStatusChange(issue.id, e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {statuses.map((s) => (
                        <option key={s.code} value={s.code}>
                          {s.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default IssuesList;

