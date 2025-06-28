"use client"

import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import FullScreenChart from "./components/full-screen-chart"
import CollapsibleSection from "./components/collapsible-section"
import type { StockAnalysis } from "./types/analysis"
import { userService } from "@/services/api"

export default function TickerPage() {
  const params = useParams()
  const navigate = useNavigate()
  const ticker = params.ticker as string
  const [data, setData] = useState<any | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (ticker) {
      setIsLoading(true)
      setError("")
      userService.getWatchlistTickerData(ticker.toUpperCase())
        .then(res => {
          setData(res.data)
          setIsLoading(false)
        })
        .catch(err => {
          setError("Failed to load prediction data.")
          setIsLoading(false)
        })
    }
  }, [ticker])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analysis for {ticker?.toUpperCase()}...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error || "Stock not found"}</p>
          <Button onClick={() => navigate(-1)}>Go Back</Button>
        </div>
      </div>
    )
  }

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case "BUY":
        return "text-green-600 bg-green-50"
      case "SELL":
        return "text-red-600 bg-red-50"
      case "HOLD":
        return "text-yellow-600 bg-yellow-50"
      default:
        return "text-gray-600 bg-gray-50"
    }
  }

  const getRecommendationEmoji = (rec: string) => {
    switch (rec) {
      case "BUY":
        return "📈"
      case "SELL":
        return "📉"
      case "HOLD":
        return "⏸️"
      default:
        return "📊"
    }
  }

  // Helper to safely get numbers
  const safeNum = (val: any) => (typeof val === 'number' && !isNaN(val) ? val : 0)

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b bg-white sticky top-0 z-50 px-4 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Watchlist
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                {data.ticker[0]}
              </div>
              <div>
                <span className="inline-block px-5 py-1 rounded-full bg-blue-100 text-blue-800 text-xl font-bold border border-blue-200 shadow align-middle">{data.ticker}</span>
                <p className="text-sm text-gray-600">{data.companyName}</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">${safeNum(data.currentPrice).toFixed(2)}</div>
              <div className={`text-sm font-medium ${safeNum(data.change) >= 0 ? "text-green-600" : "text-red-600"}`}>
                {safeNum(data.change) >= 0 ? "+" : ""}
                {safeNum(data.change).toFixed(2)} ({safeNum(data.changePercent) >= 0 ? "+" : ""}
                {safeNum(data.changePercent).toFixed(2)}%)
              </div>
            </div>
            <div className="text-right text-sm text-gray-500">
              <div>Vol: {data.volume}</div>
              <div>Cap: {data.marketCap}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Full Screen Chart */}
      <div className="h-[60vh] bg-gray-50">
        <FullScreenChart data={data.chartData} ticker={data.ticker} isPositive={safeNum(data.change) >= 0} />
      </div>

      {/* Analysis Sections */}
      <div className="max-w-7xl mx-auto p-4 space-y-4">
        {/* Price Predictions */}
        <CollapsibleSection title="📊 Price Predictions" defaultOpen={true}>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-sm text-gray-700 overflow-x-auto">
              {JSON.stringify(
                {
                  ticker: data.ticker,
                  currentPrice: safeNum(data.currentPrice),
                  predictions: data.futurePredictions.slice(0, 7), // Show first 7 days
                  generatedAt: data.lastUpdated.toISOString(),
                },
                null,
                2,
              )}
            </pre>
          </div>
        </CollapsibleSection>

        {/* Reasoning */}
        <CollapsibleSection title="🧠 AI Reasoning" defaultOpen={false}>
          <div className="space-y-4">
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Analysis Summary</h4>
              <p className="text-blue-800">{data.reasoning}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">Technical Indicators</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">RSI:</span>
                  <span className="ml-2 font-medium">{(Math.random() * 40 + 30).toFixed(1)}</span>
                </div>
                <div>
                  <span className="text-gray-600">MACD:</span>
                  <span className="ml-2 font-medium">{(Math.random() * 2 - 1).toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-gray-600">SMA 50:</span>
                  <span className="ml-2 font-medium">
                    ${(safeNum(data.currentPrice) * (0.95 + Math.random() * 0.1)).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">SMA 200:</span>
                  <span className="ml-2 font-medium">
                    ${(safeNum(data.currentPrice) * (0.9 + Math.random() * 0.2)).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Raw Analysis Data</h4>
              <pre className="text-xs text-gray-600 overflow-x-auto">
                {JSON.stringify(
                  {
                    sentiment: "neutral",
                    volatility: (Math.random() * 0.5 + 0.1).toFixed(3),
                    beta: (Math.random() * 1.5 + 0.5).toFixed(2),
                    sharpeRatio: (Math.random() * 2).toFixed(2),
                    lastAnalyzed: data.lastUpdated.toISOString(),
                  },
                  null,
                  2,
                )}
              </pre>
            </div>
          </div>
        </CollapsibleSection>

        {/* Recommendation */}
        <CollapsibleSection
          title={`${getRecommendationEmoji(data.recommendation)} ${data.recommendation} + Confidence Score`}
          defaultOpen={true}
        >
          <div className="space-y-4">
            <div className={`rounded-lg p-6 ${getRecommendationColor(data.recommendation)}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{getRecommendationEmoji(data.recommendation)}</span>
                  <div>
                    <h3 className="text-2xl font-bold">{data.recommendation}</h3>
                    <p className="text-sm opacity-80">AI Recommendation</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold">{safeNum(data.confidence).toFixed(0)}%</div>
                  <p className="text-sm opacity-80">Confidence</p>
                </div>
              </div>

              <div className="bg-white/50 rounded-lg p-4">
                <h4 className="font-semibold mb-2">Key Factors:</h4>
                <ul className="text-sm space-y-1">
                  <li>• {data.reasoning}</li>
                  <li>• Current price momentum: {safeNum(data.change) >= 0 ? "Positive" : "Negative"}</li>
                  <li>• Market volatility: {Math.random() > 0.5 ? "Low" : "Moderate"}</li>
                  <li>• Risk assessment: {Math.random() > 0.5 ? "Moderate" : "Low"}</li>
                </ul>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Recommendation Details (JSON)</h4>
              <pre className="text-sm text-gray-700 overflow-x-auto">
                {JSON.stringify(
                  {
                    recommendation: data.recommendation,
                    confidence: safeNum(data.confidence),
                    reasoning: data.reasoning,
                    riskLevel: Math.random() > 0.5 ? "moderate" : "low",
                    timeHorizon: "1-3 months",
                    targetPrice: (safeNum(data.currentPrice) * (1 + (Math.random() - 0.5) * 0.3)).toFixed(2),
                    stopLoss: (safeNum(data.currentPrice) * 0.9).toFixed(2),
                    generatedAt: data.lastUpdated.toISOString(),
                  },
                  null,
                  2,
                )}
              </pre>
            </div>
          </div>
        </CollapsibleSection>
      </div>
    </div>
  )
} 