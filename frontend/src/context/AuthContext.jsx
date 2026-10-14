import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(authService.getCurrentUser());
  const [token, setToken] = useState(authService.getToken());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleLogoutEvent = () => {
      setUser(null);
      setToken(null);
    };

    window.addEventListener('trackit_logout', handleLogoutEvent);

    // Verify token freshness with /auth/me if token exists
    if (token) {
      authService.getMe()
        .then((userData) => {
          setUser(userData);
          localStorage.setItem('trackit_user', JSON.stringify(userData));
        })
        .catch(() => {
          authService.logout();
          setUser(null);
          setToken(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }

    return () => {
      window.removeEventListener('trackit_logout', handleLogoutEvent);
    };
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setUser(data.user);
    setToken(data.access_token);
    return data;
  };

  const register = async (payload) => {
    return authService.register(payload);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
  };

  const value = {
    user,
    token,
    role: user?.role || null,
    isAuthenticated: !!token && !!user,
    isEmployee: user?.role === 'EMPLOYEE',
    isAgent: user?.role === 'SUPPORT_AGENT',
    isAdmin: user?.role === 'ADMIN',
    isSupportOrAdmin: user?.role === 'SUPPORT_AGENT' || user?.role === 'ADMIN',
    loading,
    login,
    register,
    logout,
    refreshUser: async () => {
      try {
        const u = await authService.getMe();
        setUser(u);
        localStorage.setItem('trackit_user', JSON.stringify(u));
      } catch {
        // ignore
      }
    }
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
