import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  if (!user) {
    return children;
  }

  const menuItems = [
    { path: '/', label: 'Главная' },
    { path: '/issues', label: 'Заявки' },
    { path: '/projects', label: 'Проекты' },
    { path: '/users', label: 'Пользователи' },
    { path: '/accounts', label: 'Аккаунты' },
    { path: '/companies', label: 'Компании' },
    { path: '/services', label: 'Услуги' },
    { path: '/databases', label: 'Базы данных' },
  ];

  return (
    <div className="layout">
      {/* Боковое меню слева */}
      <aside className="sidebar">
        {/* Логотип с переходом на главную */}
        <div className="sidebar-header">
          <Link to="/" className="logo">
            <span className="logo-text">Task Track</span>
          </Link>
        </div>

        {/* Навигационное меню */}
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
            >
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Информация о пользователе и выход внизу sidebar */}
        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-name">{user.name || user.email}</span>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            Выход
          </button>
        </div>
      </aside>

      {/* Основной контент справа */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;



