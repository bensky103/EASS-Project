import { useEffect, useState } from 'react';
import { userService, stockService } from '../services/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function Watchlist() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [dataMap, setDataMap] = useState<Record<string, Array<{ date: string; price: number }>>>({});
  const [newSymbol, setNewSymbol] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    userService.getWatchlist()
      .then(res => setSymbols(res.data))
      .catch(() => setError('Failed to load watchlist'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    symbols.forEach(symbol => {
      if (!dataMap[symbol]) {
        stockService.getStockData(symbol)
          .then(res => {
            setDataMap(prev => ({ ...prev, [symbol]: res.data }));
          })
          .catch(() => setError(`Failed to load data for ${symbol}`));
      }
    });
  }, [symbols]);

  const handleAdd = async () => {
    try {
      await userService.addToWatchlist(newSymbol.toUpperCase());
      setSymbols(prev => [...prev, newSymbol.toUpperCase()]);
      setNewSymbol('');
      setError(null);
    } catch {
      setError(`Failed to add ${newSymbol}`);
    }
  };

  const handleRemove = async (symbol: string) => {
    try {
      await userService.removeFromWatchlist(symbol);
      setSymbols(prev => prev.filter(s => s !== symbol));
      setError(null);
    } catch {
      setError(`Failed to remove ${symbol}`);
    }
  };

  // page-level spinner
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <svg
          className="animate-spin h-12 w-12 text-blue-600"
          xmlns="http://www.w3.org/2000/svg"
          fill="none" viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25" cx="12" cy="12" r="10"
            stroke="currentColor" strokeWidth="4"
          />
          <path
            className="opacity-75" fill="currentColor"
            d="M4 12a8 8 0 018-8v8H4z"
          />
        </svg>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">My Watchlist</h1>
      {error && <div className="text-red-600">{error}</div>}

      <div className="flex space-x-2">
        <input
          type="text"
          placeholder="Ticker (e.g. AAPL)"
          value={newSymbol}
          onChange={e => setNewSymbol(e.target.value)}
          className="border p-2 flex-1 dark:bg-gray-800 dark:border-gray-600"
        />
        <button
          onClick={handleAdd}
          className="bg-blue-600 text-white px-4 rounded"
        >
          Add
        </button>
      </div>

      {symbols.length === 0 && (
        <p className="text-gray-600">Your watchlist is empty. Add a stock above.</p>
      )}

      {symbols.map(symbol => {
        const chartData = dataMap[symbol];
        return (
          <div key={symbol} className="border p-4 rounded space-y-2">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-medium">{symbol}</h2>
              <button
                onClick={() => handleRemove(symbol)}
                className="text-red-600 hover:underline"
              >
                Remove
              </button>
            </div>

            { !chartData ? (
              <div className="flex items-center justify-center h-40">
                <svg
                  className="animate-spin h-8 w-8 text-blue-600"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none" viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25" cx="12" cy="12" r="10"
                    stroke="currentColor" strokeWidth="4"
                  />
                  <path
                    className="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8v8H4z"
                  />
                </svg>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={['auto', 'auto']} />
                  <Tooltip />
                  <Line type="monotone" dataKey="price" stroke="#2563EB" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        );
      })}
    </div>
  );
}
