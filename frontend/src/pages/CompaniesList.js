import React, { useState, useEffect } from 'react';
import { companiesAPI } from '../services/api';
import './ListPages.css';

const CompaniesList = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const response = await companiesAPI.list();
      setCompanies(response.data.results || response.data);
    } catch (error) {
      console.error('Ошибка загрузки компаний:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="list-page">
      <div className="page-header">
        <h1>Компании</h1>
      </div>
      <div className="items-grid">
        {companies.length === 0 ? (
          <div className="empty">Нет компаний</div>
        ) : (
          companies.map((company) => (
            <div key={company.id} className="item-card">
              <h3>{company.name}</h3>
              {company.code && <p>Код: {company.code}</p>}
              {company.tax_code && <p>ИНН: {company.tax_code}</p>}
              {company.content && <p>{company.content.substring(0, 100)}...</p>}
              <div className="item-meta">
                {company.owner_name && <span>Проект: {company.owner_name}</span>}
                <span>
                  Создана: {new Date(company.date_create).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CompaniesList;

