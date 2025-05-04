import axios from 'axios';

const API_URL   = import.meta.env.VITE_API_URL;
const AUTH_URL  = `${API_URL}/auth`;
const USER_URL  = `${API_URL}/user`;
const STOCK_URL = `${API_URL}/stock`;

const api = axios.create({ baseURL: API_URL });

// Attach token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to /login on 401 (expired token)
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const authService = {
  login:    (email: string, password: string) => api.post(`${AUTH_URL}/login`,    { email, password }),
  register: (email: string, password: string) => api.post(`${AUTH_URL}/register`, { email, password }),
};

export const userService = {
  getWatchlist:       () => api.get<string[]>(`${USER_URL}/watchlist`),
  addToWatchlist:     (symbol: string) => api.post(`${USER_URL}/watchlist`, { symbol }),
  removeFromWatchlist: (symbol: string) =>
    api.delete(`${USER_URL}/watchlist/${encodeURIComponent(symbol)}`),
};

export const stockService = {
  getStockData: (symbol: string) =>
    api.get<Array<{ date: string; price: number }>>(`${STOCK_URL}/${symbol}`),
};

export default api;
