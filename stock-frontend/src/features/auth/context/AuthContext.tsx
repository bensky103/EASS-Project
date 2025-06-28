import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthState } from '../types';
import { authApi } from '../api/authApi';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface AuthContextProps extends AuthState {
  login: (identifier: string, password: string, redirectTo?: string) => Promise<void>;
  register: (userData: any, redirectTo?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const isAuthenticated = !!user && !!user.id && !!token;

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setToken(storedToken);
    }
    setIsLoading(false);
  }, []);

  const fetchUserInfo = async (jwt: string) => {
    const res = await axios.get('/auth/me', {
      headers: { Authorization: `Bearer ${jwt}` },
    });
    return res.data;
  };

  const login = async (identifier: string, password: string, redirectTo?: string) => {
    setIsLoading(true);
    try {
      const res = await authApi.login(identifier, password);
      setToken(res.access_token);
      localStorage.setItem('token', res.access_token);
      // Fetch user info (with id)
      const userInfo = await fetchUserInfo(res.access_token);
      setUser(userInfo);
      localStorage.setItem('user', JSON.stringify(userInfo));
      if (redirectTo) {
        navigate(redirectTo, { replace: true });
      } else {
        navigate(`/landing/${userInfo.id}`, { replace: true });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: any, redirectTo?: string) => {
    setIsLoading(true);
    try {
      await authApi.register(userData);
      // After successful registration, log in to get the token
      await login(userData.email, userData.password, redirectTo);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    navigate('/login', { replace: true });
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
} 