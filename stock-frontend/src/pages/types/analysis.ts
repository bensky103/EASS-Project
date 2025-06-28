export interface StockAnalysis {
  ticker: string
  companyName: string
  currentPrice: number
  change: number
  changePercent: number
  chartData: ChartData[]
  futurePredictions: PricePrediction[]
  reasoning: {
    summary: string
    factors: string[]
    risks: string[]
  }
  recommendation: "BUY" | "SELL" | "HOLD"
  confidence: number
  lastUpdated: Date
  marketCap: string
  volume: string
  technicalIndicators: {
    rsi: number
    macd: number
    sma50: number
    sma200: number
    bollinger: {
      upper: number
      middle: number
      lower: number
    }
    volume: number
  }
  keyMetrics: {
    peRatio: number
    pbRatio: number
    debtToEquity: number
    roe: number
    dividendYield: number
    beta: number
  }
}

export interface ChartData {
  time: number
  price: number
}

export interface PricePrediction {
  date: string
  predictedPrice: number
  confidence: number
} 