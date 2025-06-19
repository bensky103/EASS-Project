import axios from 'axios';
import type { User } from '../types';

const API_URL = import.meta.env.VITE_API_URL;

export const authApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to set token getter (to be called from context)
let getToken: (() => string | null) | null = null;
export const setAuthTokenGetter = (getter: () => string | null) => {
  getToken = getter;
};

authApi.interceptors.request.use(config => {
  if (getToken) {
    const token = getToken();
    if (token) {
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return config;
});

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  try {
    const response = await authApi.post<AuthResponse>('/auth/register', data);
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error;
  }
};

export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  try {
    const response = await authApi.post<AuthResponse>('/auth/login', data);
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error;
  }
}; 