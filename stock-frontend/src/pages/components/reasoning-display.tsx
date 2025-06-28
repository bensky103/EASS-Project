"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, AlertTriangle, TrendingUp, BarChart3 } from "lucide-react"

interface ReasoningDisplayProps {
  reasoning: {
    summary: string
    factors: string[]
    risks: string[]
  }
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

export default function ReasoningDisplay({ reasoning, technicalIndicators, keyMetrics }: ReasoningDisplayProps) {
  const getRSIStatus = (rsi: number) => {
    if (rsi > 70) return { status: "Overbought", color: "text-red-600 bg-red-50" }
    if (rsi < 30) return { status: "Oversold", color: "text-green-600 bg-green-50" }
    return { status: "Neutral", color: "text-gray-600 bg-gray-50" }
  }

  const rsiStatus = getRSIStatus(technicalIndicators.rsi)

  return (
    <div className="space-y-6">
      {/* Analysis Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            Analysis Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 leading-relaxed">{reasoning.summary}</p>
        </CardContent>
      </Card>

      {/* Technical Indicators */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-600" />
            Technical Indicators
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">RSI (14)</div>
              <div className="font-semibold">{technicalIndicators.rsi.toFixed(1)}</div>
              <Badge className={`text-xs mt-1 ${rsiStatus.color}`}>{rsiStatus.status}</Badge>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">MACD</div>
              <div className={`font-semibold ${technicalIndicators.macd >= 0 ? "text-green-600" : "text-red-600"}`}>{technicalIndicators.macd.toFixed(2)}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">SMA 50</div>
              <div className="font-semibold">${technicalIndicators.sma50.toFixed(2)}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">SMA 200</div>
              <div className="font-semibold">${technicalIndicators.sma200.toFixed(2)}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">Volume</div>
              <div className="font-semibold">{technicalIndicators.volume.toFixed(1)}M</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">Bollinger Mid</div>
              <div className="font-semibold">${technicalIndicators.bollinger.middle.toFixed(2)}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Key Financial Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">P/E Ratio</div>
              <div className="font-semibold">{keyMetrics.peRatio.toFixed(1)}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">P/B Ratio</div>
              <div className="font-semibold">{keyMetrics.pbRatio.toFixed(2)}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">Debt/Equity</div>
              <div className="font-semibold">{keyMetrics.debtToEquity.toFixed(2)}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">ROE</div>
              <div className="font-semibold">{keyMetrics.roe.toFixed(1)}%</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">Dividend Yield</div>
              <div className="font-semibold">{keyMetrics.dividendYield.toFixed(2)}%</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-600">Beta</div>
              <div className="font-semibold">{keyMetrics.beta.toFixed(2)}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 