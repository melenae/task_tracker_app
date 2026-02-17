import React, { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';
import './ListPages.css';

const UsersList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await usersAPI.list();
      setUsers(response.data.results || response.data);
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="list-page">
      <div className="page-header">
        <h1>Пользователи</h1>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Email</th>
            <th>Роль</th>
            <th>Телефон</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr>
              <td colSpan="5" className="empty">Нет пользователей</td>
            </tr>
          ) : (
            users.map((user) => (
              <tr key={user.id}>
                <td>#{user.id}</td>
                <td>{user.name || '-'}</td>
                <td>{user.email || '-'}</td>
                <td>{user.role === 'admin' ? 'Администратор' : 'Пользователь'}</td>
                <td>{user.phone || '-'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default UsersList;





