import { createContext, useContext, useState, ReactNode } from 'react';
import { User, AuthState, LoginRequest, RegisterRequest, AuthResponse } from '../types';
import { login as apiLogin, register as apiRegister, setAuthTokenGetter } from '../api/authApi';

interface AuthContextProps extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Provide token to Axios interceptor
  setAuthTokenGetter(() => token);

  const isAuthenticated = !!user && !!token;

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data: LoginRequest = { email, password };
      const res: AuthResponse = await apiLogin(data);
      setUser(res.user);
      setToken(res.token);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, confirmPassword: string) => {
    setIsLoading(true);
    try {
      const data: RegisterRequest = { email, password, confirmPassword };
      const res: AuthResponse = await apiRegister(data);
      setUser(res.user);
      setToken(res.token);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}; 