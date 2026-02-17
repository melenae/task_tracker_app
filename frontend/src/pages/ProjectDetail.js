import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { projectsAPI, accountsAPI, usersAPI } from '../services/api';
import './ProjectDetail.css';

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [projectRes, accountsRes, usersRes] = await Promise.all([
        projectsAPI.get(id),
        accountsAPI.list(),
        usersAPI.list(),
      ]);
      setProject(projectRes.data);
      setAccounts(accountsRes.data.results || accountsRes.data || []);
      setUsers(usersRes.data.results || usersRes.data || []);
      setEditData(projectRes.data);
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      alert('Не удалось загрузить проект');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await projectsAPI.update(id, editData);
      setShowEditForm(false);
      loadData();
    } catch (error) {
      console.error('Ошибка сохранения:', error);
      alert('Не удалось сохранить изменения: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить этот проект?')) {
      return;
    }

    try {
      await projectsAPI.delete(id);
      navigate('/projects');
    } catch (error) {
      alert('Не удалось удалить проект');
    }
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (!project) {
    return <div className="error">Проект не найден</div>;
  }

  return (
    <div className="project-detail">
      <div className="project-header">
        <Link to="/projects" className="back-link">← Назад к списку</Link>
        <div className="project-actions">
          <button onClick={() => setShowEditForm(!showEditForm)}>
            {showEditForm ? 'Отмена' : 'Редактировать'}
          </button>
          <button onClick={handleDelete} className="btn-danger">
            Удалить
          </button>
        </div>
      </div>

      {showEditForm ? (
        <div className="edit-form">
          <h2>Редактирование проекта</h2>
          
          <div className="form-group">
            <label>Название проекта *</label>
            <input
              type="text"
              value={editData.name || ''}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>Описание</label>
            <textarea
              value={editData.description || ''}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              rows="5"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Аккаунт (Owner) *</label>
              <select
                value={editData.owner || ''}
                onChange={(e) => setEditData({ ...editData, owner: e.target.value })}
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
                value={editData.manager || ''}
                onChange={(e) => setEditData({ ...editData, manager: e.target.value || null })}
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
            <button onClick={handleSave} className="btn btn-primary">
              Сохранить
            </button>
            <button onClick={() => setShowEditForm(false)} className="btn">
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <div className="project-info">
          <h1>{project.name}</h1>
          
          <div className="project-details">
            <div className="detail-item">
              <strong>Описание:</strong>
              <p>{project.description || 'Не указано'}</p>
            </div>
            
            <div className="detail-item">
              <strong>Аккаунт (Owner):</strong> {project.owner_name || 'Не указан'}
            </div>
            
            <div className="detail-item">
              <strong>Менеджер:</strong> {project.manager_name || 'Не назначен'}
            </div>
            
            <div className="detail-item">
              <strong>Создан:</strong> {new Date(project.created_at).toLocaleString('ru-RU')}
            </div>
            
            <div className="detail-item">
              <strong>Обновлен:</strong> {new Date(project.updated_at).toLocaleString('ru-RU')}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectDetail;




