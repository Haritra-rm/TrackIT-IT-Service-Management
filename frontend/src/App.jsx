import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { LoadingSpinner } from './components/LoadingSpinner';

// Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { EmployeeDashboard } from './pages/EmployeeDashboard';
import { AgentDashboard } from './pages/AgentDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { TicketsList } from './pages/TicketsList';
import { CreateTicket } from './pages/CreateTicket';
import { TicketDetails } from './pages/TicketDetails';
import { UsersManagement } from './pages/UsersManagement';
import { CategoriesManagement } from './pages/CategoriesManagement';
import { Reports } from './pages/Reports';
import { AuditLogs } from './pages/AuditLogs';
import { Profile } from './pages/Profile';

// App Layout with Sidebar and Navbar
const AppLayout = () => {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <Navbar />
        <Outlet />
      </div>
    </div>
  );
};

// Protected Route Guard
const ProtectedRoute = ({ allowedRoles = [] }) => {
  const { isAuthenticated, loading, role } = useAuth();

  if (loading) {
    return <LoadingSpinner message="Authenticating session..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

// Role-Aware Dynamic Root Dashboard
const RootDashboard = () => {
  const { isAdmin, isAgent } = useAuth();
  if (isAdmin) return <AdminDashboard />;
  if (isAgent) return <AgentDashboard />;
  return <EmployeeDashboard />;
};

export const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Application Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<RootDashboard />} />
              <Route path="/tickets" element={<TicketsList />} />
              <Route path="/tickets/create" element={<CreateTicket />} />
              <Route path="/tickets/:id" element={<TicketDetails />} />
              <Route path="/profile" element={<Profile />} />

              {/* Support Agent & Admin Routes */}
              <Route element={<ProtectedRoute allowedRoles={['SUPPORT_AGENT', 'ADMIN']} />}>
                <Route path="/reports" element={<Reports />} />
              </Route>

              {/* Admin Only Routes */}
              <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
                <Route path="/users" element={<UsersManagement />} />
                <Route path="/categories" element={<CategoriesManagement />} />
                <Route path="/audit-logs" element={<AuditLogs />} />
              </Route>
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};
