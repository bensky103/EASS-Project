"use client"

import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import FullScreenChart from "./components/full-screen-chart"
import CollapsibleSection from "./components/collapsible-section"
import PredictionTable from "./components/prediction-table"
import ReasoningDisplay from "./components/reasoning-display"
import RecommendationCard from "./components/recommendation-card"
import { userService } from "@/services/api"

export default function StockAnalysisPage() {
  const params = useParams()
  const navigate = useNavigate()
  const ticker = params.ticker as string
  const [data, setData] = useState<any | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (ticker) {
      setIsLoading(true)
      userService.getWatchlistTickerData(ticker)
        .then(res => {
          setData(res.data)
          setIsLoading(false)
        })
        .catch(() => {
          setData(null)
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

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Stock not found</p>
          <Button onClick={() => navigate(-1)}>Go Back</Button>
        </div>
      </div>
    )
  }

  // Prepare chart data from price_predictions (1 week)
  let chartData: { time: number, price: number }[] = []
  if (data.price_predictions) {
    chartData = Object.entries(data.price_predictions).map(([date, price]) => ({
      time: new Date(date).getTime(),
      price: Number(price)
    }))
  }
  const latestPrice = chartData.length > 0 ? chartData[chartData.length - 1].price : 0
  const volume = data.volume || data.technical_indicators?.volume || 0

  return (
    <div className="min-h-screen bg-gray-50">
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
                {ticker[0]}
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{ticker}</h1>
                <p className="text-sm text-gray-600">{data.companyName || ticker}</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">${latestPrice.toFixed(2)}</div>
            </div>
            <div className="text-right text-sm text-gray-500">
              <div>Vol: {volume}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Full Screen Chart */}
      <div className="h-[60vh] bg-white border-b">
        <FullScreenChart data={chartData} ticker={ticker} isPositive={chartData.length > 1 && chartData[0].price <= chartData[chartData.length - 1].price} />
      </div>

      {/* Analysis Sections */}
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Price Predictions */}
        {chartData.length > 0 && (
          <CollapsibleSection title="📊 Price Predictions" defaultOpen={true}>
            <PredictionTable predictions={chartData.map((d, i) => ({ date: new Date(d.time).toISOString().split('T')[0], predictedPrice: d.price, confidence: data.confidence || 0 })).slice(0, 7)} currentPrice={latestPrice} />
          </CollapsibleSection>
        )}

        {/* AI Reasoning */}
        <CollapsibleSection title="🧠 AI Reasoning" defaultOpen={false}>
          <ReasoningDisplay
            reasoning={data.reasoning}
            technicalIndicators={data.technical_indicators}
            keyMetrics={data.key_metrics}
          />
        </CollapsibleSection>

        {/* Recommendation */}
        <CollapsibleSection
          title={`${getRecommendationEmoji(data.recommendation)} ${data.recommendation} + Confidence Score`}
          defaultOpen={true}
        >
          <RecommendationCard
            recommendation={data.recommendation}
            confidence={data.confidence}
            reasoning={data.reasoning}
            currentPrice={latestPrice}
          />
        </CollapsibleSection>
      </div>
    </div>
  )
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