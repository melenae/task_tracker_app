import React, { useState, useEffect } from 'react';
import { servicesAPI } from '../services/api';
import './ListPages.css';

const ServicesList = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    try {
      const response = await servicesAPI.list();
      setServices(response.data.results || response.data);
    } catch (error) {
      console.error('Ошибка загрузки услуг:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="list-page">
      <div className="page-header">
        <h1>Услуги</h1>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Цена</th>
            <th>Время проверки</th>
            <th>Время дедлайна</th>
            <th>Компания</th>
            <th>Создана</th>
          </tr>
        </thead>
        <tbody>
          {services.length === 0 ? (
            <tr>
              <td colSpan="6" className="empty">Нет услуг</td>
            </tr>
          ) : (
            services.map((service) => (
              <tr key={service.id}>
                <td>#{service.id}</td>
                <td>{service.price || '-'}</td>
                <td>{service.time_check || '-'}</td>
                <td>{service.time_dead_line || '-'}</td>
                <td>{service.company_name || '-'}</td>
                <td>{new Date(service.date_create).toLocaleDateString('ru-RU')}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ServicesList;

