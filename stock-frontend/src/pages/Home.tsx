import { useState } from 'react'
import api from '../services/api'

export default function Home() {
  const [symbol, setSymbol] = useState('AAPL')
  const [history, setHistory] = useState('150,152,151,153,155,157,156,158,160,162')
  const [result, setResult] = useState<{ predicted_price: number; confidence: number } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const historical_data = history
        .split(',')
        .map(s => parseFloat(s.trim()))
        .filter(n => !isNaN(n))

      const { data } = await api.post('/predict', { stock_symbol: symbol, historical_data })
      setResult(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Prediction failed')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Stock Price Prediction Model</h1>
      <p className="text-gray-700 dark:text-gray-300">
        We’ve trained a GRU neural network to forecast the next-day closing price
        of a stock based on its last 10 days of prices. Enter a symbol and a
        comma-separated list of historical prices to see the model’s prediction
        and confidence.
      </p>

      {/* spinner overlay */}
      {loading && (
        <div className="fixed inset-0 bg-white/50 dark:bg-black/50 flex items-center justify-center">
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
      )}

      <form onSubmit={handleSubmit} className="space-y-4 relative">
        <div>
          <label className="block font-medium">Stock Symbol</label>
          <input
            type="text"
            value={symbol}
            onChange={e => setSymbol(e.target.value.toUpperCase())}
            className="w-full border rounded p-2 dark:bg-gray-800 dark:border-gray-600"
            required
          />
        </div>

        <div>
          <label className="block font-medium">Historical Data</label>
          <textarea
            value={history}
            onChange={e => setHistory(e.target.value)}
            className="w-full border rounded p-2 h-20 dark:bg-gray-800 dark:border-gray-600"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white py-2 px-4 rounded disabled:opacity-50"
        >
          {loading ? 'Predicting…' : 'Try a Prediction'}
        </button>
      </form>

      {error && <div className="text-red-600 font-medium">{error}</div>}

      {result && (
        <div className="mt-6 p-4 border rounded bg-green-50 dark:bg-green-900">
          <p>
            <span className="font-medium">Predicted Price:</span> $
            {result.predicted_price.toFixed(2)}
          </p>
          <p>
            <span className="font-medium">Confidence:</span>{' '}
            {(result.confidence * 100).toFixed(1)}%
          </p>
        </div>
      )}
    </div>
  )
}
