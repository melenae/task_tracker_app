import React, { useState, useEffect } from 'react';
import { accountsAPI } from '../services/api';
import './ListPages.css';

const AccountsList = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await accountsAPI.list();
      setAccounts(response.data.results || response.data || []);
    } catch (error) {
      console.error('Ошибка загрузки аккаунтов:', error);
      if (error.response?.status === 403) {
        alert('Недостаточно прав для просмотра аккаунтов');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="list-page">
      <div className="page-header">
        <h1>Аккаунты</h1>
      </div>
      <div className="items-grid">
        {accounts.length === 0 ? (
          <div className="empty">Нет аккаунтов</div>
        ) : (
          accounts.map((account) => (
            <div key={account.id} className="item-card">
              <h3>{account.name || account.slug}</h3>
              {account.content && <p>{account.content.substring(0, 100)}...</p>}
              <div className="item-meta">
                <span>Slug: {account.slug}</span>
                <span>
                  Создан: {new Date(account.date_create).toLocaleDateString('ru-RU')}
                </span>
                {account.user_name && <span>Менеджер: {account.user_name}</span>}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AccountsList;

