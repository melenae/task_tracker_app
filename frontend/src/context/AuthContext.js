import React, { createContext, useState, useEffect, useContext } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password);
      console.log('Login response:', response.data);
      
      // Проверяем успешность логина
      if (response.data && response.data.success) {
        // После успешного логина получаем полную информацию о пользователе
        try {
          const userResponse = await authAPI.getCurrentUser();
          setUser(userResponse.data);
        } catch (err) {
          console.warn('Could not get user profile, using basic info:', err);
          // Если не удалось получить профиль, используем базовую информацию
          if (response.data.user) {
            setUser(response.data.user);
          }
        }
        return { success: true };
      } else {
        // Если success не true, значит ошибка
        return {
          success: false,
          error: response.data?.error || 'Login failed',
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error response:', error.response);
      
      // Обрабатываем разные типы ошибок
      let errorMessage = 'Login failed';
      if (error.response) {
        // Сервер вернул ответ с ошибкой
        errorMessage = error.response.data?.error || 
                      error.response.data?.detail || 
                      `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Запрос был отправлен, но ответа не получено
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Ошибка при настройке запроса
        errorMessage = error.message || 'Login failed';
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

