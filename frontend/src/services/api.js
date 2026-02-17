import axios from 'axios';

// Используем абсолютный URL для API, чтобы не зависеть от proxy
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Создаем экземпляр axios с базовыми настройками
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Для работы с сессиями Django
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Перенаправление на логин при 401
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/login/', { email, password }),
  logout: () => api.post('/logout/'),
  getCurrentUser: () => api.get('/current-user/'),
};

// Dashboard API
export const dashboardAPI = {
  getData: () => api.get('/dashboard/'),
};

// Issues API
export const issuesAPI = {
  list: (params) => api.get('/issues/', { params }),
  get: (id) => api.get(`/issues/${id}/`),
  create: (data) => api.post('/issues/', data),
  update: (id, data) => api.patch(`/issues/${id}/`, data),
  delete: (id) => api.delete(`/issues/${id}/`),
  updateStatus: (id, status) => api.patch(`/issues/${id}/`, { status }),
};

// Projects API
export const projectsAPI = {
  list: (params) => api.get('/projects/', { params }),
  get: (id) => api.get(`/projects/${id}/`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.patch(`/projects/${id}/`, data),
  delete: (id) => api.delete(`/projects/${id}/`),
};

// Users API
export const usersAPI = {
  list: (params) => api.get('/users/', { params }),
  get: (id) => api.get(`/users/${id}/`),
  create: (data) => api.post('/users/', data),
  update: (id, data) => api.patch(`/users/${id}/`, data),
  delete: (id) => api.delete(`/users/${id}/`),
};

// Accounts API
export const accountsAPI = {
  list: (params) => api.get('/accounts/', { params }),
  get: (id) => api.get(`/accounts/${id}/`),
  create: (data) => api.post('/accounts/', data),
  update: (id, data) => api.patch(`/accounts/${id}/`, data),
  delete: (id) => api.delete(`/accounts/${id}/`),
};

// Companies API
export const companiesAPI = {
  list: (params) => api.get('/companies/', { params }),
  get: (id) => api.get(`/companies/${id}/`),
  create: (data) => api.post('/companies/', data),
  update: (id, data) => api.patch(`/companies/${id}/`, data),
  delete: (id) => api.delete(`/companies/${id}/`),
};

// Services API
export const servicesAPI = {
  list: (params) => api.get('/services/', { params }),
  get: (id) => api.get(`/services/${id}/`),
  create: (data) => api.post('/services/', data),
  update: (id, data) => api.patch(`/services/${id}/`, data),
  delete: (id) => api.delete(`/services/${id}/`),
};

// Databases API
export const databasesAPI = {
  list: (params) => api.get('/databases/', { params }),
  get: (id) => api.get(`/databases/${id}/`),
  create: (data) => api.post('/databases/', data),
  update: (id, data) => api.patch(`/databases/${id}/`, data),
  delete: (id) => api.delete(`/databases/${id}/`),
};

// Comments API
export const commentsAPI = {
  list: (params) => api.get('/comments/', { params }),
  create: (data) => api.post('/comments/', data),
  update: (id, data) => api.patch(`/comments/${id}/`, data),
  delete: (id) => api.delete(`/comments/${id}/`),
};

// Project Teams API
export const projectTeamsAPI = {
  list: (params) => api.get('/project-teams/', { params }),
  create: (data) => api.post('/project-teams/', data),
  update: (id, data) => api.patch(`/project-teams/${id}/`, data),
  delete: (id) => api.delete(`/project-teams/${id}/`),
};

// Client Teams API
export const clientTeamsAPI = {
  list: (params) => api.get('/client-teams/', { params }),
  create: (data) => api.post('/client-teams/', data),
  update: (id, data) => api.patch(`/client-teams/${id}/`, data),
  delete: (id) => api.delete(`/client-teams/${id}/`),
};

export default api;


