import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Minus, Target, Shield } from "lucide-react"

interface RecommendationCardProps {
  recommendation: "BUY" | "SELL" | "HOLD"
  confidence: number
  reasoning: {
    summary: string
    factors: string[]
    risks: string[]
  }
  currentPrice: number
}

export default function RecommendationCard({
  recommendation,
  confidence,
  reasoning,
  currentPrice,
}: RecommendationCardProps) {
  const getRecommendationConfig = (rec: string) => {
    switch (rec) {
      case "BUY":
        return {
          color: "text-green-600 bg-green-50 border-green-200",
          bgColor: "bg-green-50",
          textColor: "text-green-800",
          icon: TrendingUp,
          emoji: "📈",
        }
      case "SELL":
        return {
          color: "text-red-600 bg-red-50 border-red-200",
          bgColor: "bg-red-50",
          textColor: "text-red-800",
          icon: TrendingDown,
          emoji: "📉",
        }
      case "HOLD":
        return {
          color: "text-yellow-600 bg-yellow-50 border-yellow-200",
          bgColor: "bg-yellow-50",
          textColor: "text-yellow-800",
          icon: Minus,
          emoji: "⏸️",
        }
      default:
        return {
          color: "text-gray-600 bg-gray-50 border-gray-200",
          bgColor: "bg-gray-50",
          textColor: "text-gray-800",
          icon: Minus,
          emoji: "📊",
        }
    }
  }

  const config = getRecommendationConfig(recommendation)
  const Icon = config.icon

  const getTargetPrice = () => {
    const multiplier = recommendation === "BUY" ? 1.15 : recommendation === "SELL" ? 0.85 : 1.05
    return currentPrice * multiplier
  }

  const getStopLoss = () => {
    return currentPrice * 0.9
  }

  const getConfidenceLevel = (conf: number) => {
    if (conf >= 80) return { level: "High", color: "text-green-600 bg-green-100" }
    if (conf >= 60) return { level: "Medium", color: "text-yellow-600 bg-yellow-100" }
    return { level: "Low", color: "text-red-600 bg-red-100" }
  }

  const confidenceLevel = getConfidenceLevel(confidence)

  return (
    <div className="space-y-6">
      {/* Main Recommendation Card */}
      <Card className={`border-2 ${config.color}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-full ${config.bgColor} flex items-center justify-center`}>
                <span className="text-3xl">{config.emoji}</span>
              </div>
              <div>
                <h3 className={`text-3xl font-bold ${config.textColor}`}>{recommendation}</h3>
                <p className="text-sm text-gray-600">AI Recommendation</p>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-4xl font-bold ${config.textColor}`}>{confidence.toFixed(0)}%</div>
              <Badge className={confidenceLevel.color}>{confidenceLevel.level} Confidence</Badge>
            </div>
          </div>

          <div className={`${config.bgColor} rounded-lg p-4 mb-4`}>
            <p className={`${config.textColor} font-medium`}>{reasoning.summary}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4 border">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-gray-600">Target Price</span>
              </div>
              <div className="text-xl font-bold text-gray-900">${getTargetPrice().toFixed(2)}</div>
              <div className="text-sm text-gray-500">
                {(((getTargetPrice() - currentPrice) / currentPrice) * 100).toFixed(1)}% upside
              </div>
            </div>

            <div className="bg-white rounded-lg p-4 border">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-red-600" />
                <span className="text-sm font-medium text-gray-600">Stop Loss</span>
              </div>
              <div className="text-xl font-bold text-gray-900">${getStopLoss().toFixed(2)}</div>
              <div className="text-sm text-gray-500">
                {(((getStopLoss() - currentPrice) / currentPrice) * 100).toFixed(1)}% downside
              </div>
            </div>

            <div className="bg-white rounded-lg p-4 border">
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-gray-600">Time Horizon</span>
              </div>
              <div className="text-xl font-bold text-gray-900">1-3M</div>
              <div className="text-sm text-gray-500">Short to medium term</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Plan */}
      <Card>
        <CardContent className="p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Recommended Action Plan</h4>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                1
              </div>
              <div>
                <p className="font-medium">Entry Strategy</p>
                <p className="text-sm text-gray-600">
                  {recommendation === "BUY"
                    ? "Consider dollar-cost averaging over 2-3 weeks to reduce timing risk"
                    : recommendation === "SELL"
                      ? "Consider gradual position reduction to minimize market impact"
                      : "Monitor key support/resistance levels for better entry/exit points"}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                2
              </div>
              <div>
                <p className="font-medium">Risk Management</p>
                <p className="text-sm text-gray-600">
                  Set stop-loss at ${getStopLoss().toFixed(2)} and monitor position size relative to portfolio
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                3
              </div>
              <div>
                <p className="font-medium">Review Timeline</p>
                <p className="text-sm text-gray-600">
                  Reassess position after next earnings report or significant market events
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
