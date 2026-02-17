import React, { useState, useEffect } from 'react';
import { databasesAPI } from '../services/api';
import './ListPages.css';

const DatabasesList = () => {
  const [databases, setDatabases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDatabases();
  }, []);

  const loadDatabases = async () => {
    try {
      const response = await databasesAPI.list();
      setDatabases(response.data.results || response.data);
    } catch (error) {
      console.error('Ошибка загрузки баз данных:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="list-page">
      <div className="page-header">
        <h1>Базы данных</h1>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Путь</th>
            <th>Сервер</th>
            <th>Компания</th>
            <th>Комментарий</th>
            <th>Создана</th>
          </tr>
        </thead>
        <tbody>
          {databases.length === 0 ? (
            <tr>
              <td colSpan="6" className="empty">Нет баз данных</td>
            </tr>
          ) : (
            databases.map((db) => (
              <tr key={db.id}>
                <td>#{db.id}</td>
                <td>{db.path || '-'}</td>
                <td>{db.server || '-'}</td>
                <td>{db.company_name || '-'}</td>
                <td>{db.comment ? (db.comment.length > 50 ? db.comment.substring(0, 50) + '...' : db.comment) : '-'}</td>
                <td>{new Date(db.date_create).toLocaleDateString('ru-RU')}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DatabasesList;

