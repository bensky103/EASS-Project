export interface StockPrediction {
  id: string
  ticker: string
  companyName: string
  currentPrice: number
  change: number
  changePercent: number
  prediction: "bullish" | "bearish"
  confidence: number
  chartData: ChartData[]
  lastUpdated: Date
  logo: string
}

export interface ChartData {
  time: number
  price: number
}

export interface PredictionResponse {
  predictions: StockPrediction[]
  timestamp: string
  status: "success" | "error"
}
