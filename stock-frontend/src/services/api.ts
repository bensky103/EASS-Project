import axios from 'axios';

const api = axios.create();

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
  login:    (email: string, password: string) => api.post(`/auth/login`,    { email, password }),
  register: (email: string, password: string) => api.post(`/auth/register`, { email, password }),
};

export const userService = {
  getWatchlist:       () => api.get<string[]>(`/user/watchlist`),
  addToWatchlist:     (symbol: string) => api.post(`/user/watchlist`, { symbol }),
  removeFromWatchlist: (symbol: string) =>
    api.delete(`/user/watchlist/${encodeURIComponent(symbol)}`),
  getPredictions:     () => api.get(`/user/predictions`),
  getWatchlistData:   () => api.get(`/user/watchlist/data`),
  getWatchlistTickerData: (ticker: string) => api.get(`/user/watchlist/${encodeURIComponent(ticker)}`),
};

export const stockService = {
  getStockData: (symbol: string) =>
    api.get<Array<{ date: string; price: number }>>(`/stock/${symbol}`),
};

export const predictService = {
  predict: (ticker: string) => api.post('/llm_service/predict', { symbol: ticker }),
};

export default api;
