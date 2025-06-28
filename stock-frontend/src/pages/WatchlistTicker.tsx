import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import FullScreenChart from "./components/full-screen-chart"
import CollapsibleSection from "./components/collapsible-section"
import PredictionTable from "./components/prediction-table"
import ReasoningDisplay from "./components/reasoning-display"
import RecommendationCard from "./components/recommendation-card"
import type { StockAnalysis } from "./types/analysis"
import { userService } from "@/services/api"

// ... (rest of the StockAnalysisPage code from src/app/watchlist/[ticker]/page.tsx, replacing router.back() with navigate(-1))

const generateStockAnalysis = (ticker: string): StockAnalysis => {
  return null as any;
}

const getCompanyName = (ticker: string): string => {
  return "";
}

const generateDetailedReasoning = (ticker: string, recommendation: string) => {
  return "";
}

const generateTechnicalIndicators = (basePrice: number) => ({
  // ... existing code ...
})

const generateKeyMetrics = () => ({
  // ... existing code ...
})

export default function WatchlistTicker() {
  const params = useParams()
  const navigate = useNavigate()
  const userId = params.userId as string
  const ticker = params.ticker as string
  const [analysis, setAnalysis] = useState<StockAnalysis | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (ticker) {
      setIsLoading(true)
      setError(null)
      userService.getWatchlistTickerData(ticker)
        .then(res => {
          if (res.data) {
            const p = res.data;
            const pred = p.prediction || {};
            const fetched = p.fetchedStockData || {};
            // Prefer prediction, fallback to fetched, then root
            const ti = pred.technical_indicators || fetched.technical_indicators || p.technical_indicators || {};
            const vf = pred.volume_features || fetched.volume_features || p.volume_features || {};
            const f = pred.fundamentals || fetched.fundamentals || p.fundamentals || {};
            const news = pred.news_sentiment || fetched.news_sentiment || p.news_sentiment || {};
            const extTi = pred.technical_indicators_ext || fetched.technical_indicators_ext || p.technical_indicators_ext || {};
            const extVf = pred.volume_features_ext || fetched.volume_features_ext || p.volume_features_ext || {};
            const advNews = pred.advanced_news_sentiment || fetched.advanced_news_sentiment || p.advanced_news_sentiment || {};
            const extFund = pred.extended_fundamentals || fetched.extended_fundamentals || p.extended_fundamentals || {};
            const price_predictions = pred.price_predictions || fetched.price_predictions || p.price_predictions || {};
            const recommendation = pred.recommendation || fetched.recommendation || p.recommendation || 'HOLD';
            const confidence = pred.confidence ?? fetched.confidence ?? p.confidence ?? 0;
            const reasoning = pred.reasoning || fetched.reasoning || p.reasoning || { summary: 'No summary available.', factors: [], risks: [] };
            const timestamp = pred.timestamp || fetched.timestamp || p.timestamp || new Date().toISOString();
            const symbol = pred.symbol || fetched.symbol || p.symbol || ticker.toUpperCase();
            // Generate chartData with zig-zag effect for demo
            const chartData = Object.entries(price_predictions).map(([date, price], i) => {
              const basePrice = Number(price);
              // Zig-zag: amplitude 3% of price, frequency based on i
              const amplitude = 0.03 * basePrice;
              const zigzag = amplitude * Math.sin(i * 1.5);
              return {
                time: new Date(date).getTime(),
                price: basePrice + zigzag,
              };
            });
            const futurePredictions = Object.entries(price_predictions).map(([date, price]) => ({
              date,
              predictedPrice: Number(price),
              confidence: confidence
            }));
            setAnalysis({
              ticker: symbol,
              companyName: '',
              currentPrice: ti.latest_close ?? 0,
              change: ((ti.latest_close ?? 0) - (ti.open ?? 0)),
              changePercent: ti.open ? (((ti.latest_close ?? 0) - ti.open) / ti.open) * 100 : 0,
              volume: vf.latest_volume ?? ti.volume ?? 0,
              marketCap: f.market_cap ?? 0,
              chartData,
              futurePredictions,
              reasoning: typeof reasoning === 'string' ? { summary: reasoning, factors: [], risks: [] } : reasoning,
              technicalIndicators: {
                rsi: ti.rsi ?? 0,
                macd: ti.macd ?? 0,
                sma50: ti.sma_5 ?? 0,
                sma200: ti.sma_5 ?? 0,
                bollinger: {
                  upper: ti.bb_upper ?? 0,
                  middle: ti.bb_middle ?? 0,
                  lower: ti.bb_lower ?? 0,
                },
                volume: vf.latest_volume ?? ti.volume ?? 0,
              },
              keyMetrics: {
                peRatio: f.pe_ratio ?? 0,
                pbRatio: 0,
                debtToEquity: extFund.debt_equity_ratio ?? 0,
                roe: extFund.roe ?? 0,
                dividendYield: f.dividend_yield ?? 0,
                beta: f.beta ?? 0,
              },
              recommendation,
              confidence,
              lastUpdated: new Date(timestamp),
            });
          } else {
            setAnalysis(null);
          }
          setIsLoading(false);
        })
        .catch(err => {
          setError("Stock not found in your watchlist.");
          setIsLoading(false);
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

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error || "Stock not found"}</p>
          <Button onClick={() => navigate(`/watchlist/${userId}`)}>Go Back</Button>
        </div>
      </div>
    )
  }

  // Debug: Log confidence value
  console.log('CONFIDENCE:', analysis.confidence);

  // Debug: Log confidence value before passing to RecommendationCard
  console.log('CONFIDENCE passed to RecommendationCard:', analysis.confidence);

  // Determine if the price is positive (up) for the chart color
  const isPositive = analysis && analysis.chartData && analysis.chartData.length > 1
    ? analysis.chartData[analysis.chartData.length - 1].price >= analysis.chartData[0].price
    : true;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header bar above the chart */}
      <div className="w-full flex items-center justify-between px-6 py-4 bg-white border-b">
        {/* Left: Back Button */}
        <div>
          <Button variant="ghost" size="sm" onClick={() => navigate(`/watchlist/${userId}`)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Watchlist
          </Button>
        </div>
        {/* Center: Ticker Name */}
        <div className="flex-1 flex justify-center">
          <span className="text-2xl font-bold text-gray-900">{analysis.ticker}</span>
        </div>
        {/* Right: Price and Volume */}
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">${analysis.currentPrice?.toFixed(2)}</div>
          <div className="text-sm text-gray-500">Vol: {analysis.volume}</div>
        </div>
      </div>
      {/* Chart below header */}
      <div className="h-[60vh] bg-white">
        <FullScreenChart data={analysis.chartData || []} ticker={analysis.ticker} isPositive={isPositive} />
      </div>

      {/* Analysis Sections */}
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Price Predictions */}
        <CollapsibleSection title="📊 Price Predictions" defaultOpen={true}>
          <PredictionTable predictions={analysis.futurePredictions?.slice(0, 14) || []} currentPrice={analysis.currentPrice} />
        </CollapsibleSection>

        {/* AI Reasoning */}
        <CollapsibleSection title="🧠 AI Reasoning" defaultOpen={false}>
          <ReasoningDisplay
            reasoning={analysis.reasoning}
            technicalIndicators={analysis.technicalIndicators}
            keyMetrics={analysis.keyMetrics}
          />
        </CollapsibleSection>

        {/* Recommendation */}
        <CollapsibleSection
          title={`${getRecommendationEmoji(analysis.recommendation)} ${analysis.recommendation} + Confidence Score`}
          defaultOpen={true}
        >
          <RecommendationCard
            recommendation={analysis.recommendation}
            confidence={analysis.confidence}
            reasoning={analysis.reasoning}
            currentPrice={analysis.currentPrice}
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