"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, RefreshCw, Minus } from "lucide-react"
import { Button } from "@/components/ui/button"
import StockChart from "./components/stock-chart"
import type { StockPrediction } from "../../app/watchlist/types/stock"
import { Link } from "react-router-dom"
import { userService } from "@/services/api"
import { useAuth } from "../features/auth/context/AuthContext"
import { useNavigate } from "react-router-dom"

export default function WatchlistPage() {
  const [watchlistData, setWatchlistData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const { user } = useAuth()
  const navigate = useNavigate()

  const fetchWatchlistData = async () => {
    setIsLoading(true)
    try {
      const res = await userService.getWatchlistData()
      const dataArr = Array.isArray(res.data) ? res.data : []
      setWatchlistData(dataArr)
    } catch (err) {
      setWatchlistData([])
    }
    setLastUpdate(new Date())
    setIsLoading(false)
  }

  useEffect(() => {
    fetchWatchlistData()
  }, [])

  const refreshWatchlist = fetchWatchlistData

  if (!user) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          {/* Navigation Bar */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b">
            <div className="flex items-center gap-2">
              <button
                className="text-blue-600 hover:text-blue-800 text-sm font-medium px-2 py-1 rounded flex items-center"
                onClick={() => navigate(user ? `/landing/${user.id}` : "/landing")}
                style={{ marginRight: '1rem' }}
              >
                &#8592; Back
              </button>
              <TrendingUp className="h-6 w-6" />
              <span className="text-lg font-bold">StockAI Pro</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-700 font-semibold">Welcome {user?.username || user?.email || "User"}</span>
            </div>
          </div>

          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Stock Watchlist</h1>
              <p className="text-gray-600 mt-1">AI-powered predictions updated in real-time</p>
            </div>
            <div className="flex gap-3">
              <Button onClick={refreshWatchlist} disabled={isLoading}>
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
                Refresh
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              {watchlistData.length} stocks tracked
            </Badge>
          </div>
        </div>

        {/* Watchlist Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {watchlistData.map((data) => {
            // Robustly extract data from possible nesting
            const fetched = data.fetchedStockData || data.fetched || {};
            const prediction = data.prediction || {};
            const ticker = data.ticker || fetched.ticker || prediction.ticker || data.symbol || "?";
            // Prefer prediction price_predictions, fallback to fetched
            const pricePredictions = prediction.price_predictions || fetched.price_predictions || {};
            // Get current and predicted price
            let currentPrice = null;
            let predictedPrice = null;
            const priceEntries = Object.entries(pricePredictions);
            if (priceEntries.length > 0) {
              currentPrice = priceEntries[0][1];
              predictedPrice = priceEntries[priceEntries.length - 1][1];
            }
            // Recommendation/confidence/timestamp
            const recommendation = prediction.recommendation || fetched.recommendation || "";
            const confidence = prediction.confidence ?? fetched.confidence;
            const timestamp = prediction.timestamp || fetched.timestamp || data.timestamp || "";
            // Company name fallback
            const companyName = data.companyName || fetched.companyName || ticker;
            // Recommendation badge rendering
            let rec = (recommendation || '').toUpperCase();
            let recColor = 'bg-gray-100 text-gray-700 border-gray-200';
            if (rec === 'BUY') recColor = 'bg-green-100 text-green-800 border-green-200';
            else if (rec === 'SELL') recColor = 'bg-red-100 text-red-800 border-red-200';
            else if (rec === 'HOLD') recColor = 'bg-yellow-100 text-yellow-800 border-yellow-200';
            const recommendationBadge = (
              <span className={`inline-block px-4 py-1 rounded-full font-bold border text-base mr-2 ${recColor}`}>{rec || 'N/A'}</span>
            );
            let displayCurrentPrice = typeof currentPrice === 'number' ? `$${currentPrice.toFixed(2)}` : "-";
            let displayPredictedPrice = typeof predictedPrice === 'number' ? `$${predictedPrice.toFixed(2)}` : "-";
            return (
              <Link to={`/watchlist/${user.id}/${ticker}`} key={ticker}>
                <Card className="w-[300px] min-h-[240px] mx-auto hover:shadow-lg transition-shadow duration-200 overflow-hidden cursor-pointer">
                  <CardContent className="p-4 flex flex-col h-full items-center justify-center">
                    <div
                      className="bg-white rounded-xl shadow p-4 flex flex-col h-full items-center justify-center"
                      style={{ minWidth: 200, maxWidth: 300, minHeight: 220 }}
                    >
                      {/* Ticker badge at the top */}
                      <div className="w-full flex justify-center mb-4">
                        <span className="px-5 py-1 rounded-full bg-gray-100 text-gray-800 text-base font-bold border border-gray-300 shadow text-center">
                          {ticker}
                        </span>
                      </div>
                      {/* Current Price badge */}
                      <div className="mb-3 w-11/12 flex justify-center">
                        <span className="w-full px-4 py-3 rounded-full bg-blue-100 text-blue-800 text-base font-bold border border-blue-200 shadow text-center flex items-center justify-center">
                          <span className="mr-2">💲</span> Current Price: <span className="ml-2 font-extrabold">{displayCurrentPrice}</span>
                        </span>
                      </div>
                      {/* Predicted Price badge */}
                      <div className="mb-3 w-11/12 flex justify-center">
                        <span className="w-full px-4 py-3 rounded-full bg-purple-100 text-purple-800 text-base font-bold border border-purple-200 shadow text-center flex items-center justify-center">
                          <span className="mr-2">🔮</span> Predicted Price: <span className="ml-2 font-extrabold">{displayPredictedPrice}</span>
                        </span>
                      </div>
                      {/* Confidence badge */}
                      <div className="mb-3 w-11/12 flex justify-center">
                        <span className={`w-full px-4 py-3 rounded-full text-base font-bold border shadow text-center flex items-center justify-center ${confidence >= 0.8 ? 'bg-green-100 text-green-800 border-green-200' : confidence >= 0.6 ? 'bg-yellow-100 text-yellow-800 border-yellow-200' : 'bg-red-100 text-red-700 border-red-200'}`}>
                          <span className="mr-2">{confidence >= 0.8 ? '✅' : '⚠️'}</span> Confidence: <span className="ml-2 font-extrabold">{(confidence !== undefined && confidence !== null && !isNaN(confidence)) ? `${(confidence * 100).toFixed(0)}%` : "N/A"}</span>
                        </span>
                      </div>
                      {/* Recommendation badge */}
                      <div className="mb-1 w-11/12 flex justify-center">
                        <span className={`w-full px-4 py-3 rounded-full text-base font-bold border shadow text-center flex items-center justify-center ${rec === 'BUY' ? 'bg-green-200 text-green-900 border-green-300' : rec === 'SELL' ? 'bg-red-200 text-red-900 border-red-300' : rec === 'HOLD' ? 'bg-yellow-200 text-yellow-900 border-yellow-300' : 'bg-gray-100 text-gray-700 border-gray-200'}`}>
                          <span className="mr-2">{rec === 'BUY' ? '🟢' : rec === 'SELL' ? '🔴' : rec === 'HOLD' ? '🟡' : '⚪'}</span> Recommendation: <span className="ml-2 font-extrabold">{rec === 'BUY' ? 'BUY' : rec === 'SELL' ? 'SELL' : rec === 'HOLD' ? 'HOLD' : 'N/A'}</span>
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}
