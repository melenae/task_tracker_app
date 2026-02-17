import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { issuesAPI, usersAPI, companiesAPI, databasesAPI, servicesAPI, projectsAPI } from '../services/api';
import './IssueCreate.css';

const IssueCreate = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    content: '',
    status: 'new',
    priority: 'medium',
    companies: null,
    databases: null,
    services: null,
    users: null,
    supervisor: null,
    owner: null,
    parent: null,
    sprint: null,
    deadline: null,
    date_check: null,
    date_start_plan: null,
    date_end_plan: null,
    time_dead_line: null,
    time_check: null,
    sla_reac: null,
    sla_exec: null,
    sla_check: null,
    sla_deadline: null,
    comment: '',
    // Новые поля (заглушки для будущих полей модели)
    topic: '',
    object_system: '',
    related: null,
    emails: '',
    // Норматив
    normative_reac: null,
    normative_exec: null,
    normative_check: null,
    normative_deadline: null,
    normative_price: null,
    // План - даты
    date_start_fact: null,
    date_end_fact: null,
    date_check_fact: null,
    // План - часы
    plan_hours_total: null,
    plan_hours_analyst: null,
    plan_hours_development: null,
    plan_hours_paid: null,
    plan_sum: null,
    // Факт - часы
    fact_hours_total: null,
    fact_hours_analyst: null,
    fact_hours_development: null,
    fact_hours_paid: null,
    fact_sum: null,
    // Рабочая группа
    applicant: null,
  });
  const [users, setUsers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [databases, setDatabases] = useState([]);
  const [services, setServices] = useState([]);
  const [projects, setProjects] = useState([]);
  const [issues, setIssues] = useState([]);
  const [sprints, setSprints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      const [usersRes, companiesRes, databasesRes, servicesRes, issuesRes, projectsRes] = await Promise.all([
        usersAPI.list(),
        companiesAPI.list(),
        databasesAPI.list(),
        servicesAPI.list(),
        issuesAPI.list(),
        projectsAPI.list(),
      ]);
      setUsers(usersRes.data.results || usersRes.data || []);
      setCompanies(companiesRes.data.results || companiesRes.data || []);
      setDatabases(databasesRes.data.results || databasesRes.data || []);
      setServices(servicesRes.data.results || servicesRes.data || []);
      setIssues(issuesRes.data.results || issuesRes.data || []);
      setProjects(projectsRes.data.results || projectsRes.data || []);
      // TODO: Добавить загрузку спринтов когда будет API
      setSprints([]);
    } catch (error) {
      console.error('Ошибка загрузки опций:', error);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Преобразуем пустые строки в null для опциональных полей
      const dataToSave = { ...formData };
      
      // Очистка полей
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

      await issuesAPI.create(dataToSave);
      navigate('/issues');
    } catch (error) {
      setError(
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Не удалось создать задачу'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value || null });
  };

  return (
    <div className="issue-create">
      <h1>Создать задачу</h1>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit} className="create-form">
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
                    value="Автоматически"
                    disabled
                    className="disabled-field"
                  />
                </div>
                <div className="form-group">
                  <label>Родитель</label>
                  <select
                    value={formData.parent || ''}
                    onChange={(e) => handleChange('parent', e.target.value)}
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
                  <label>Проект *</label>
                  <select
                    value={formData.owner || ''}
                    onChange={(e) => handleChange('owner', e.target.value)}
                    required
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
                    value={formData.priority}
                    onChange={(e) => handleChange('priority', e.target.value)}
                  >
                    <option value="low">Низкий</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                  </select>
                </div>
              </div>

              {/* Строка 2: Название */}
              <div className="form-group">
                <label>Название *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  required
                />
              </div>

              {/* Строка 3: Описание */}
              <div className="form-group">
                <label>Описание</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => handleChange('content', e.target.value)}
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
                    value={formData.sprint || ''}
                    onChange={(e) => handleChange('sprint', e.target.value)}
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
                    value={formData.topic || ''}
                    onChange={(e) => handleChange('topic', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Объект системы</label>
                  <input
                    type="text"
                    value={formData.object_system || ''}
                    onChange={(e) => handleChange('object_system', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Связано</label>
                  <select
                    value={formData.related || ''}
                    onChange={(e) => handleChange('related', e.target.value)}
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
                    value={formData.emails || ''}
                    onChange={(e) => handleChange('emails', e.target.value)}
                    rows="3"
                    placeholder="Входящие Emails"
                  />
                </div>
                <div className="form-group">
                  <label>Входящие Emails</label>
                  <textarea
                    value={formData.emails || ''}
                    onChange={(e) => handleChange('emails', e.target.value)}
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
                      value={formData.sla_reac || ''}
                      onChange={(e) => handleChange('sla_reac', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Выполнение</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.sla_exec || ''}
                      onChange={(e) => handleChange('sla_exec', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-row-2">
                  <div className="form-group">
                    <label>Проверка</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.sla_check || ''}
                      onChange={(e) => handleChange('sla_check', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Дэдлайн</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.sla_deadline || ''}
                      onChange={(e) => handleChange('sla_deadline', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Статус и дата создания */}
              <div className="form-row-2">
                <div className="form-group">
                  <label>Статус</label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleChange('status', e.target.value)}
                  >
                    <option value="new">Новая</option>
                    <option value="in_progress">В работе</option>
                    <option value="waiting">Ожидает</option>
                    <option value="testing">Тестирование</option>
                    <option value="done">Выполнена</option>
                    <option value="closed">Закрыта</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Дата создания</label>
                  <input
                    type="text"
                    value="Автоматически"
                    disabled
                    className="disabled-field"
                  />
                </div>
              </div>

              {/* База данных, Организация, Услуга */}
              <div className="form-group">
                <label>База Данных</label>
                <select
                  value={formData.databases || ''}
                  onChange={(e) => handleChange('databases', e.target.value)}
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
                  value={formData.companies || ''}
                  onChange={(e) => handleChange('companies', e.target.value)}
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
                  value={formData.services || ''}
                  onChange={(e) => handleChange('services', e.target.value)}
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
                      value={formData.normative_reac || ''}
                      onChange={(e) => handleChange('normative_reac', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Выполнение</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.normative_exec || ''}
                      onChange={(e) => handleChange('normative_exec', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-row-2">
                  <div className="form-group">
                    <label>Проверка</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.normative_check || ''}
                      onChange={(e) => handleChange('normative_check', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Deadline</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.normative_deadline || ''}
                      onChange={(e) => handleChange('normative_deadline', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Цена</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.normative_price || ''}
                    onChange={(e) => handleChange('normative_price', e.target.value)}
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
                    value={formatDateTime(formData.date_start_plan)}
                    onChange={(e) => handleChange('date_start_plan', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Завершить</label>
                  <input
                    type="datetime-local"
                    value={formatDateTime(formData.date_end_plan)}
                    onChange={(e) => handleChange('date_end_plan', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Проверить</label>
                  <input
                    type="datetime-local"
                    value={formatDateTime(formData.date_check)}
                    onChange={(e) => handleChange('date_check', e.target.value)}
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
                    value={formatDateTime(formData.date_start_fact)}
                    onChange={(e) => handleChange('date_start_fact', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Завершено</label>
                  <input
                    type="datetime-local"
                    value={formatDateTime(formData.date_end_fact)}
                    onChange={(e) => handleChange('date_end_fact', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Проверено</label>
                  <input
                    type="datetime-local"
                    value={formatDateTime(formData.date_check_fact)}
                    onChange={(e) => handleChange('date_check_fact', e.target.value)}
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
                    value={formData.plan_hours_analyst || ''}
                    onChange={(e) => handleChange('plan_hours_analyst', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Разработка</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.plan_hours_development || ''}
                    onChange={(e) => handleChange('plan_hours_development', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>В т.ч. платно</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.plan_hours_paid || ''}
                    onChange={(e) => handleChange('plan_hours_paid', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Сумма</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.plan_sum || ''}
                    onChange={(e) => handleChange('plan_sum', e.target.value)}
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
                    value={formData.fact_hours_analyst || ''}
                    onChange={(e) => handleChange('fact_hours_analyst', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Разработка</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.fact_hours_development || ''}
                    onChange={(e) => handleChange('fact_hours_development', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>В т.ч. платно</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.fact_hours_paid || ''}
                    onChange={(e) => handleChange('fact_hours_paid', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Сумма</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.fact_sum || ''}
                    onChange={(e) => handleChange('fact_sum', e.target.value)}
                  />
                </div>
              </div>

              {/* Рабочая группа */}
              <div className="info-group">
                <h3 className="info-group-title">Рабочая группа</h3>
                <div className="form-group">
                  <label>Инициатор</label>
                  <select
                    value={formData.applicant || ''}
                    onChange={(e) => handleChange('applicant', e.target.value)}
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
                    value={formData.users || ''}
                    onChange={(e) => handleChange('users', e.target.value)}
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
                    value={formData.supervisor || ''}
                    onChange={(e) => handleChange('supervisor', e.target.value)}
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
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Создание...' : 'Создать задачу'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/issues')}
            className="btn btn-secondary"
          >
            Отмена
          </button>
        </div>
      </form>
    </div>
  );
};

export default IssueCreate;
