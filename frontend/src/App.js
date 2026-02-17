import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import IssuesList from './pages/IssuesList';
import IssueDetail from './pages/IssueDetail';
import IssueCreate from './pages/IssueCreate';
import ProjectsList from './pages/ProjectsList';
import ProjectDetail from './pages/ProjectDetail';
import UsersList from './pages/UsersList';
import AccountsList from './pages/AccountsList';
import CompaniesList from './pages/CompaniesList';
import ServicesList from './pages/ServicesList';
import DatabasesList from './pages/DatabasesList';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return user ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/issues"
            element={
              <PrivateRoute>
                <Layout>
                  <IssuesList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/issues/create"
            element={
              <PrivateRoute>
                <Layout>
                  <IssueCreate />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/issues/:id"
            element={
              <PrivateRoute>
                <Layout>
                  <IssueDetail />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/projects"
            element={
              <PrivateRoute>
                <Layout>
                  <ProjectsList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <PrivateRoute>
                <Layout>
                  <ProjectDetail />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/users"
            element={
              <PrivateRoute>
                <Layout>
                  <UsersList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/accounts"
            element={
              <PrivateRoute>
                <Layout>
                  <AccountsList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/companies"
            element={
              <PrivateRoute>
                <Layout>
                  <CompaniesList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/services"
            element={
              <PrivateRoute>
                <Layout>
                  <ServicesList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/databases"
            element={
              <PrivateRoute>
                <Layout>
                  <DatabasesList />
                </Layout>
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
