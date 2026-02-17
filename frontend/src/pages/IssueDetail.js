import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { issuesAPI, commentsAPI, usersAPI, companiesAPI, databasesAPI, servicesAPI, projectsAPI } from '../services/api';
import './IssueDetail.css';

const IssueDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [issue, setIssue] = useState(null);
  const [comments, setComments] = useState([]);
  const [users, setUsers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [databases, setDatabases] = useState([]);
  const [services, setServices] = useState([]);
  const [projects, setProjects] = useState([]);
  const [issues, setIssues] = useState([]);
  const [sprints, setSprints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [showEditForm, setShowEditForm] = useState(false);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [issueRes, commentsRes, usersRes, companiesRes, databasesRes, servicesRes, issuesRes, projectsRes] = await Promise.all([
        issuesAPI.get(id),
        commentsAPI.list({ issue: id }),
        usersAPI.list(),
        companiesAPI.list(),
        databasesAPI.list(),
        servicesAPI.list(),
        issuesAPI.list(),
        projectsAPI.list(),
      ]);
      setIssue(issueRes.data);
      setComments(commentsRes.data.results || commentsRes.data || []);
      setUsers(usersRes.data.results || usersRes.data || []);
      setCompanies(companiesRes.data.results || companiesRes.data || []);
      setDatabases(databasesRes.data.results || databasesRes.data || []);
      setServices(servicesRes.data.results || servicesRes.data || []);
      setIssues((issuesRes.data.results || issuesRes.data || []).filter(i => i.id !== parseInt(id)));
      setProjects(projectsRes.data.results || projectsRes.data || []);
      // TODO: Добавить загрузку спринтов когда будет API
      setSprints([]);
      // Инициализируем editData с дефолтными значениями для новых полей
      setEditData({
        ...issueRes.data,
        topic: issueRes.data.topic || '',
        object_system: issueRes.data.object_system || '',
        related: issueRes.data.related || null,
        emails: issueRes.data.emails || '',
        normative_reac: issueRes.data.normative_reac || null,
        normative_exec: issueRes.data.normative_exec || null,
        normative_check: issueRes.data.normative_check || null,
        normative_deadline: issueRes.data.normative_deadline || null,
        normative_price: issueRes.data.normative_price || null,
        date_start_fact: issueRes.data.date_start_fact || null,
        date_end_fact: issueRes.data.date_end_fact || null,
        date_check_fact: issueRes.data.date_check_fact || null,
        plan_hours_total: issueRes.data.plan_hours_total || null,
        plan_hours_analyst: issueRes.data.plan_hours_analyst || null,
        plan_hours_development: issueRes.data.plan_hours_development || null,
        plan_hours_paid: issueRes.data.plan_hours_paid || null,
        plan_sum: issueRes.data.plan_sum || null,
        fact_hours_total: issueRes.data.fact_hours_total || null,
        fact_hours_analyst: issueRes.data.fact_hours_analyst || null,
        fact_hours_development: issueRes.data.fact_hours_development || null,
        fact_hours_paid: issueRes.data.fact_hours_paid || null,
        fact_sum: issueRes.data.fact_sum || null,
        applicant: issueRes.data.applicant || null,
      });
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      alert('Не удалось загрузить задачу');
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleString('ru-RU');
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await issuesAPI.updateStatus(id, newStatus);
      loadData();
    } catch (error) {
      alert('Не удалось изменить статус');
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await commentsAPI.create({
        issue: parseInt(id),
        comment: newComment,
      });
      setNewComment('');
      loadData();
    } catch (error) {
      alert('Не удалось добавить комментарий');
    }
  };

  const handleSave = async () => {
    try {
      // Преобразуем пустые строки в null для опциональных полей
      const dataToSave = { ...editData };
      
      const fieldsToClean = [
        'companies', 'databases', 'services', 'users', 'supervisor', 'owner', 
        'parent', 'sprint', 'related', 'applicant',
        'deadline', 'date_check', 'date_start_plan', 'date_end_plan',
        'date_start_fact', 'date_end_fact', 'date_check_fact',
        'time_dead_line', 'time_check',
        'sla_reac', 'sla_exec', 'sla_check', 'sla_deadline',
        'normative_reac', 'normative_exec', 'normative_check', 'normative_deadline', 'normative_price',
        'plan_hours_total', 'plan_hours_analyst', 'plan_hours_development', 'plan_hours_paid', 'plan_sum',
        'fact_hours_total', 'fact_hours_analyst', 'fact_hours_development', 'fact_hours_paid', 'fact_sum',
        'comment', 'topic', 'object_system', 'emails'
      ];
      
      fieldsToClean.forEach(field => {
        if (dataToSave[field] === '') dataToSave[field] = null;
      });

      // Удаляем поля, которых нет в модели (временно)
      delete dataToSave.topic;
      delete dataToSave.object_system;
      delete dataToSave.related;
      delete dataToSave.emails;
      delete dataToSave.normative_reac;
      delete dataToSave.normative_exec;
      delete dataToSave.normative_check;
      delete dataToSave.normative_deadline;
      delete dataToSave.normative_price;
      delete dataToSave.date_start_fact;
      delete dataToSave.date_end_fact;
      delete dataToSave.date_check_fact;
      delete dataToSave.plan_hours_total;
      delete dataToSave.plan_hours_analyst;
      delete dataToSave.plan_hours_development;
      delete dataToSave.plan_hours_paid;
      delete dataToSave.plan_sum;
      delete dataToSave.fact_hours_total;
      delete dataToSave.fact_hours_analyst;
      delete dataToSave.fact_hours_development;
      delete dataToSave.fact_hours_paid;
      delete dataToSave.fact_sum;
      delete dataToSave.applicant;
      
      await issuesAPI.update(id, dataToSave);
      setShowEditForm(false);
      loadData();
    } catch (error) {
      console.error('Ошибка сохранения:', error);
      alert('Не удалось сохранить изменения: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (!issue) {
    return <div className="error">Задача не найдена</div>;
  }

  const statusOptions = [
    { value: 'new', label: 'Новая' },
    { value: 'in_progress', label: 'В работе' },
    { value: 'waiting', label: 'Ожидает' },
    { value: 'testing', label: 'Тестирование' },
    { value: 'done', label: 'Выполнена' },
    { value: 'closed', label: 'Закрыта' },
  ];

  return (
    <div className="issue-detail">
      <div className="issue-header">
        <Link to="/issues" className="back-link">← Назад к списку</Link>
        <div className="issue-actions">
          <button onClick={() => setShowEditForm(!showEditForm)}>
            {showEditForm ? 'Отмена' : 'Редактировать'}
          </button>
        </div>
      </div>

      {showEditForm ? (
        <div className="edit-form">
          <h2>Редактирование задачи</h2>
          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="create-form">
            <div className="form-layout">
              {/* Левая колонка */}
              <div className="form-left-column">
                {/* Группа: Сведения */}
                <div className="form-section">
                  <h2 className="section-title">Сведения</h2>
                  
                  {/* Строка 1: Код задачи, Родитель, Проект, Срочность */}
                  <div className="form-row-4">
                    <div className="form-group">
                      <label>Код задачи</label>
                      <input
                        type="text"
                        value={editData.id || ''}
                        disabled
                        className="disabled-field"
                      />
                    </div>
                    <div className="form-group">
                      <label>Родитель</label>
                      <select
                        value={editData.parent || ''}
                        onChange={(e) => setEditData({ ...editData, parent: e.target.value || null })}
                      >
                        <option value="">Не выбрано</option>
                        {issues.map((iss) => (
                          <option key={iss.id} value={iss.id}>
                            {iss.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Проект</label>
                      <select
                        value={editData.owner || ''}
                        onChange={(e) => setEditData({ ...editData, owner: e.target.value || null })}
                      >
                        <option value="">Не выбрано</option>
                        {projects.map((project) => (
                          <option key={project.id} value={project.id}>
                            {project.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Срочность</label>
                      <select
                        value={editData.priority || 'medium'}
                        onChange={(e) => setEditData({ ...editData, priority: e.target.value })}
                      >
                        <option value="low">Низкий</option>
                        <option value="medium">Средний</option>
                        <option value="high">Высокий</option>
                      </select>
                    </div>
                  </div>

                  {/* Строка 2: Название */}
                  <div className="form-group">
                    <label>Название</label>
                    <input
                      type="text"
                      value={editData.name || ''}
                      onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                    />
                  </div>

                  {/* Строка 3: Описание */}
                  <div className="form-group">
                    <label>Описание</label>
                    <textarea
                      value={editData.content || ''}
                      onChange={(e) => setEditData({ ...editData, content: e.target.value })}
                      rows="5"
                    />
                  </div>
                </div>

                {/* Группа: Подробности */}
                <div className="form-section">
                  <h2 className="section-title">Подробности</h2>
                  
                  {/* Строка 1: Sprint, Топик, Объект системы, Связано */}
                  <div className="form-row-4">
                    <div className="form-group">
                      <label>Sprint</label>
                      <select
                        value={editData.sprint || ''}
                        onChange={(e) => setEditData({ ...editData, sprint: e.target.value || null })}
                      >
                        <option value="">Не выбрано</option>
                        {sprints.map((sprint) => (
                          <option key={sprint.id} value={sprint.id}>
                            {sprint.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Топик</label>
                      <input
                        type="text"
                        value={editData.topic || ''}
                        onChange={(e) => setEditData({ ...editData, topic: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Объект системы</label>
                      <input
                        type="text"
                        value={editData.object_system || ''}
                        onChange={(e) => setEditData({ ...editData, object_system: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Связано</label>
                      <select
                        value={editData.related || ''}
                        onChange={(e) => setEditData({ ...editData, related: e.target.value || null })}
                      >
                        <option value="">Не выбрано</option>
                        {issues.map((iss) => (
                          <option key={iss.id} value={iss.id}>
                            {iss.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Письма и входящие Emails */}
                  <div className="form-row">
                    <div className="form-group">
                      <label>Письма</label>
                      <textarea
                        value={editData.emails || ''}
                        onChange={(e) => setEditData({ ...editData, emails: e.target.value })}
                        rows="3"
                        placeholder="Входящие Emails"
                      />
                    </div>
                    <div className="form-group">
                      <label>Входящие Emails</label>
                      <textarea
                        value={editData.emails || ''}
                        onChange={(e) => setEditData({ ...editData, emails: e.target.value })}
                        rows="3"
                        placeholder="Входящие Emails"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Правая колонка: Информация */}
              <div className="form-right-column">
                <div className="form-section">
                  <h2 className="section-title">Информация</h2>
                  
                  {/* SLA */}
                  <div className="info-group">
                    <h3 className="info-group-title">SLA</h3>
                    <div className="form-row-2">
                      <div className="form-group">
                        <label>Реакция</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.sla_reac || ''}
                          onChange={(e) => setEditData({ ...editData, sla_reac: e.target.value || null })}
                        />
                      </div>
                      <div className="form-group">
                        <label>Выполнение</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.sla_exec || ''}
                          onChange={(e) => setEditData({ ...editData, sla_exec: e.target.value || null })}
                        />
                      </div>
                    </div>
                    <div className="form-row-2">
                      <div className="form-group">
                        <label>Проверка</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.sla_check || ''}
                          onChange={(e) => setEditData({ ...editData, sla_check: e.target.value || null })}
                        />
                      </div>
                      <div className="form-group">
                        <label>Дэдлайн</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.sla_deadline || ''}
                          onChange={(e) => setEditData({ ...editData, sla_deadline: e.target.value || null })}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Статус и дата создания */}
                  <div className="form-row-2">
                    <div className="form-group">
                      <label>Статус</label>
                      <select
                        value={editData.status || 'new'}
                        onChange={(e) => setEditData({ ...editData, status: e.target.value })}
                      >
                        {statusOptions.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Дата создания</label>
                      <input
                        type="text"
                        value={formatDate(editData.date_create)}
                        disabled
                        className="disabled-field"
                      />
                    </div>
                  </div>

                  {/* База данных, Организация, Услуга */}
                  <div className="form-group">
                    <label>База Данных</label>
                    <select
                      value={editData.databases || ''}
                      onChange={(e) => setEditData({ ...editData, databases: e.target.value || null })}
                    >
                      <option value="">Не выбрано</option>
                      {databases.map((db) => (
                        <option key={db.id} value={db.id}>
                          {db.path} - {db.server}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Организация</label>
                    <select
                      value={editData.companies || ''}
                      onChange={(e) => setEditData({ ...editData, companies: e.target.value || null })}
                    >
                      <option value="">Не выбрано</option>
                      {companies.map((company) => (
                        <option key={company.id} value={company.id}>
                          {company.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Услуга</label>
                    <select
                      value={editData.services || ''}
                      onChange={(e) => setEditData({ ...editData, services: e.target.value || null })}
                    >
                      <option value="">Не выбрано</option>
                      {services.map((service) => (
                        <option key={service.id} value={service.id}>
                          {service.name || `Услуга #${service.id}`}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Норматив */}
                  <div className="info-group">
                    <h3 className="info-group-title">Норматив</h3>
                    <div className="form-row-2">
                      <div className="form-group">
                        <label>Реакция</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.normative_reac || ''}
                          onChange={(e) => setEditData({ ...editData, normative_reac: e.target.value || null })}
                        />
                      </div>
                      <div className="form-group">
                        <label>Выполнение</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.normative_exec || ''}
                          onChange={(e) => setEditData({ ...editData, normative_exec: e.target.value || null })}
                        />
                      </div>
                    </div>
                    <div className="form-row-2">
                      <div className="form-group">
                        <label>Проверка</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.normative_check || ''}
                          onChange={(e) => setEditData({ ...editData, normative_check: e.target.value || null })}
                        />
                      </div>
                      <div className="form-group">
                        <label>Deadline</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editData.normative_deadline || ''}
                          onChange={(e) => setEditData({ ...editData, normative_deadline: e.target.value || null })}
                        />
                      </div>
                    </div>
                    <div className="form-group">
                      <label>Цена</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.normative_price || ''}
                        onChange={(e) => setEditData({ ...editData, normative_price: e.target.value || null })}
                      />
                    </div>
                  </div>

                  {/* План - Начать, Завершить, Проверить */}
                  <div className="info-group">
                    <h3 className="info-group-title">План</h3>
                    <div className="form-group">
                      <label>Начать</label>
                      <input
                        type="datetime-local"
                        value={formatDateTime(editData.date_start_plan)}
                        onChange={(e) => setEditData({ ...editData, date_start_plan: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Завершить</label>
                      <input
                        type="datetime-local"
                        value={formatDateTime(editData.date_end_plan)}
                        onChange={(e) => setEditData({ ...editData, date_end_plan: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Проверить</label>
                      <input
                        type="datetime-local"
                        value={formatDateTime(editData.date_check)}
                        onChange={(e) => setEditData({ ...editData, date_check: e.target.value || null })}
                      />
                    </div>
                  </div>

                  {/* Факт - Начато, Завершено, Проверено */}
                  <div className="info-group">
                    <h3 className="info-group-title">Факт</h3>
                    <div className="form-group">
                      <label>Начато</label>
                      <input
                        type="datetime-local"
                        value={formatDateTime(editData.date_start_fact)}
                        onChange={(e) => setEditData({ ...editData, date_start_fact: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Завершено</label>
                      <input
                        type="datetime-local"
                        value={formatDateTime(editData.date_end_fact)}
                        onChange={(e) => setEditData({ ...editData, date_end_fact: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Проверено</label>
                      <input
                        type="datetime-local"
                        value={formatDateTime(editData.date_check_fact)}
                        onChange={(e) => setEditData({ ...editData, date_check_fact: e.target.value || null })}
                      />
                    </div>
                  </div>

                  {/* План - часы */}
                  <div className="info-group">
                    <h3 className="info-group-title">План - ч.:</h3>
                    <div className="form-group">
                      <label>Аналитик</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.plan_hours_analyst || ''}
                        onChange={(e) => setEditData({ ...editData, plan_hours_analyst: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Разработка</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.plan_hours_development || ''}
                        onChange={(e) => setEditData({ ...editData, plan_hours_development: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>В т.ч. платно</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.plan_hours_paid || ''}
                        onChange={(e) => setEditData({ ...editData, plan_hours_paid: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Сумма</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.plan_sum || ''}
                        onChange={(e) => setEditData({ ...editData, plan_sum: e.target.value || null })}
                      />
                    </div>
                  </div>

                  {/* Факт - часы */}
                  <div className="info-group">
                    <h3 className="info-group-title">Факт - ч.:</h3>
                    <div className="form-group">
                      <label>Аналитик</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.fact_hours_analyst || ''}
                        onChange={(e) => setEditData({ ...editData, fact_hours_analyst: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Разработка</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.fact_hours_development || ''}
                        onChange={(e) => setEditData({ ...editData, fact_hours_development: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>В т.ч. платно</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.fact_hours_paid || ''}
                        onChange={(e) => setEditData({ ...editData, fact_hours_paid: e.target.value || null })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Сумма</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.fact_sum || ''}
                        onChange={(e) => setEditData({ ...editData, fact_sum: e.target.value || null })}
                      />
                    </div>
                  </div>

                  {/* Рабочая группа */}
                  <div className="info-group">
                    <h3 className="info-group-title">Рабочая группа</h3>
                    <div className="form-group">
                      <label>Инициатор</label>
                      <select
                        value={editData.applicant || ''}
                        onChange={(e) => setEditData({ ...editData, applicant: e.target.value || null })}
                      >
                        <option value="">Не выбрано</option>
                        {users.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.name || user.email}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Ответственный</label>
                      <select
                        value={editData.users || ''}
                        onChange={(e) => setEditData({ ...editData, users: e.target.value || null })}
                      >
                        <option value="">Не выбрано</option>
                        {users.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.name || user.email}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Контролер</label>
                      <select
                        value={editData.supervisor || ''}
                        onChange={(e) => setEditData({ ...editData, supervisor: e.target.value || null })}
                      >
                        <option value="">Не выбрано</option>
                        {users.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.name || user.email}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                Сохранить
              </button>
              <button type="button" onClick={() => setShowEditForm(false)} className="btn btn-secondary">
                Отмена
              </button>
            </div>
          </form>
        </div>
      ) : (
        <>
          <div className="issue-info">
            <h1>{issue.name}</h1>
            <div className="issue-meta">
              <div className="meta-item">
                <strong>Статус:</strong>
                <select
                  value={issue.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                >
                  {statusOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="meta-item">
                <strong>Приоритет:</strong> {issue.priority || 'Не указан'}
              </div>
              <div className="meta-item">
                <strong>Создана:</strong> {formatDate(issue.date_create)}
              </div>
            </div>

            <div className="issue-details-grid">
              <div className="detail-item">
                <strong>Проект:</strong> {issue.owner_name || 'Не указан'}
              </div>
              <div className="detail-item">
                <strong>Компания:</strong> {issue.companies_name || 'Не указана'}
              </div>
              <div className="detail-item">
                <strong>База данных:</strong> {issue.databases_path || 'Не указана'}
              </div>
              <div className="detail-item">
                <strong>Услуга:</strong> {issue.services_name || 'Не указана'}
              </div>
              <div className="detail-item">
                <strong>Исполнитель:</strong> {issue.users_name || 'Не назначен'}
              </div>
              <div className="detail-item">
                <strong>Супервайзер:</strong> {issue.supervisor_name || 'Не назначен'}
              </div>
              <div className="detail-item">
                <strong>Родительская задача:</strong> {issue.parent_name || 'Нет'}
              </div>
              {issue.deadline && (
                <div className="detail-item">
                  <strong>Срок выполнения:</strong> {formatDate(issue.deadline)}
                </div>
              )}
              {issue.date_check && (
                <div className="detail-item">
                  <strong>Дата проверки:</strong> {formatDate(issue.date_check)}
                </div>
              )}
              {issue.date_start_plan && (
                <div className="detail-item">
                  <strong>Дата начала планирования:</strong> {formatDate(issue.date_start_plan)}
                </div>
              )}
              {issue.date_end_plan && (
                <div className="detail-item">
                  <strong>Дата окончания планирования:</strong> {formatDate(issue.date_end_plan)}
                </div>
              )}
              {issue.time_dead_line && (
                <div className="detail-item">
                  <strong>Время дедлайна:</strong> {issue.time_dead_line}
                </div>
              )}
              {issue.time_check && (
                <div className="detail-item">
                  <strong>Время проверки:</strong> {issue.time_check}
                </div>
              )}
              {issue.sla_reac && (
                <div className="detail-item">
                  <strong>СЛА реакции:</strong> {issue.sla_reac}
                </div>
              )}
              {issue.sla_exec && (
                <div className="detail-item">
                  <strong>СЛА выполнения:</strong> {issue.sla_exec}
                </div>
              )}
              {issue.sla_check && (
                <div className="detail-item">
                  <strong>СЛА проверки:</strong> {issue.sla_check}
                </div>
              )}
              {issue.sla_deadline && (
                <div className="detail-item">
                  <strong>СЛА дедлайна:</strong> {issue.sla_deadline}
                </div>
              )}
            </div>

            {issue.content && (
              <div className="issue-content">
                <h3>Описание</h3>
                <p>{issue.content}</p>
              </div>
            )}

            {issue.comment && (
              <div className="issue-comment">
                <h3>Комментарий</h3>
                <p>{issue.comment}</p>
              </div>
            )}
          </div>

          <div className="comments-section">
            <h2>Комментарии ({comments.length})</h2>
            <form onSubmit={handleAddComment} className="comment-form">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Добавить комментарий..."
                rows="3"
              />
              <button type="submit" className="btn btn-primary">
                Добавить комментарий
              </button>
            </form>
            <div className="comments-list">
              {comments.length === 0 ? (
                <p className="no-comments">Комментариев пока нет</p>
              ) : (
                comments.map((comment) => (
                  <div key={comment.id} className="comment">
                    <div className="comment-header">
                      <strong>{comment.author_name || 'Пользователь'}</strong>
                      <span className="comment-date">
                        {formatDate(comment.date_create)}
                      </span>
                    </div>
                    <div className="comment-content">{comment.comment}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default IssueDetail;
