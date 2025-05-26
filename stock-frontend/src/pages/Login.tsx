// src/pages/Login.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { data } = await authService.login(email, password);
      localStorage.setItem('token', data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-sm mx-auto p-4">
      <h2 className="text-xl mb-4 dark:text-white">Login</h2>

      {error && <div className="text-red-600 mb-2">{error}</div>}

      <label className="block mb-2 dark:text-white">
        Email
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="w-full border p-2 dark:bg-gray-800 dark:border-gray-600"
          required
        />
      </label>

      <label className="block mb-4 dark:text-white">
        Password
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full border p-2 dark:bg-gray-800 dark:border-gray-600"
          required
        />
      </label>

      <button
        style={{ transform: 'translateY(3px)', color: 'black' }}
        type="submit"
        className="w-full bg-blue-600 dark:bg-white text-white dark:text-black p-2 rounded"
      >
        Login
      </button>
    </form>
  );
}
