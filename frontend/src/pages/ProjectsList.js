import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { projectsAPI, accountsAPI, usersAPI } from '../services/api';
import './ListPages.css';

const ProjectsList = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    owner: '',
    manager: null,
  });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [projectsRes, accountsRes, usersRes] = await Promise.all([
        projectsAPI.list(),
        accountsAPI.list(),
        usersAPI.list(),
      ]);
      setProjects(projectsRes.data.results || projectsRes.data || []);
      setAccounts(accountsRes.data.results || accountsRes.data || []);
      setUsers(usersRes.data.results || usersRes.data || []);
    } catch (error) {
      console.error('Ошибка загрузки проектов:', error);
      if (error.response?.status === 403) {
        alert('Недостаточно прав для просмотра проектов');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);

    try {
      const dataToSave = {
        ...formData,
        manager: formData.manager || null,
      };
      await projectsAPI.create(dataToSave);
      setShowCreateForm(false);
      setFormData({ name: '', description: '', owner: '', manager: null });
      loadData();
    } catch (error) {
      alert('Не удалось создать проект: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="list-page">
      <div className="page-header">
        <h1>Проекты</h1>
        <button onClick={() => setShowCreateForm(!showCreateForm)} className="btn btn-primary">
          {showCreateForm ? 'Отмена' : '+ Создать проект'}
        </button>
      </div>

      {showCreateForm && (
        <div className="create-form-container">
          <h2>Создать новый проект</h2>
          <form onSubmit={handleCreate} className="create-form">
            <div className="form-group">
              <label>Название проекта *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows="3"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Аккаунт (Owner) *</label>
                <select
                  value={formData.owner}
                  onChange={(e) => setFormData({ ...formData, owner: e.target.value })}
                  required
                >
                  <option value="">Выберите аккаунт</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.name || account.slug}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Менеджер</label>
                <select
                  value={formData.manager || ''}
                  onChange={(e) => setFormData({ ...formData, manager: e.target.value || null })}
                >
                  <option value="">Не назначен</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.name || user.email}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" disabled={creating} className="btn btn-primary">
                {creating ? 'Создание...' : 'Создать'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setFormData({ name: '', description: '', owner: '', manager: null });
                }}
                className="btn btn-secondary"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="items-grid">
        {projects.length === 0 ? (
          <div className="empty">Нет проектов</div>
        ) : (
          projects.map((project) => (
            <div key={project.id} className="item-card">
              <div className="item-card-header">
                <h3>
                  <Link to={`/projects/${project.id}`}>{project.name}</Link>
                </h3>
                <button
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="btn-edit"
                >
                  Редактировать
                </button>
              </div>
              {project.description && <p>{project.description}</p>}
              <div className="item-meta">
                <span>Аккаунт: {project.owner_name || 'Не указан'}</span>
                <span>Менеджер: {project.manager_name || 'Не назначен'}</span>
                <span>
                  Создан: {new Date(project.created_at).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ProjectsList;
