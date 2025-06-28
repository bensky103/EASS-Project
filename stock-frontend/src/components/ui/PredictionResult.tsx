import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Target, Clock, BarChart3 } from "lucide-react"

interface PredictionResultProps {
  prediction: any // Use 'any' for now, or define a new type for the LLM response
  currentPrice?: number | null
}

export default function PredictionResult({ prediction, currentPrice }: PredictionResultProps) {
  const safeStr = (val: any) => (val === undefined || val === null ? "N/A" : val)
  const confidencePct = prediction.confidence !== undefined && prediction.confidence !== null && !isNaN(prediction.confidence)
    ? (Number(prediction.confidence) * 100).toFixed(1) + "%"
    : "N/A"
  const pricePreds = prediction.price_predictions ? Object.entries(prediction.price_predictions) : []
  const firstPrice = typeof currentPrice === 'number' ? currentPrice : (pricePreds.length > 0 && typeof pricePreds[0][1] === 'number' ? pricePreds[0][1] as number : null);
  const lastPrice = pricePreds.length > 0 && typeof pricePreds[pricePreds.length - 1][1] === 'number' ? pricePreds[pricePreds.length - 1][1] as number : null;
  const priceChange = (typeof firstPrice === 'number' && typeof lastPrice === 'number') ? (lastPrice - firstPrice) : null;
  const percentChange = (priceChange !== null && typeof firstPrice === 'number' && firstPrice !== 0) ? (priceChange / firstPrice) * 100 : null;

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl font-bold flex items-center">
            <BarChart3 className="mr-2 h-6 w-6 text-blue-600" />
            {safeStr(prediction.symbol || prediction.ticker)} Prediction Results
          </CardTitle>
          <Badge variant={prediction.recommendation === "BUY" ? "default" : prediction.recommendation === "SELL" ? "destructive" : "secondary"} className="text-sm font-semibold">
            {prediction.recommendation || "N/A"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Current Price (first in price_predictions) */}
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Current Price</div>
            <div className="text-2xl font-bold text-gray-900">
              {firstPrice !== null ? `$${Number(firstPrice).toFixed(2)}` : "N/A"}
            </div>
          </div>

          {/* Predicted Price (last in price_predictions) */}
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-blue-600 mb-1 flex items-center justify-center">
              <Target className="mr-1 h-4 w-4" />
              Predicted Price
            </div>
            <div className="text-2xl font-bold text-blue-900">
              {lastPrice !== null ? `$${Number(lastPrice).toFixed(2)}` : "N/A"}
            </div>
          </div>

          {/* Price Change */}
          <div className={`text-center p-4 rounded-lg ${priceChange !== null && priceChange >= 0 ? "bg-green-50" : "bg-red-50"}`}>
            <div
              className={`text-sm mb-1 flex items-center justify-center ${
                priceChange !== null && priceChange >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {priceChange !== null && priceChange >= 0 ? <TrendingUp className="mr-1 h-4 w-4" /> : <TrendingDown className="mr-1 h-4 w-4" />}
              Expected Change
            </div>
            <div className={`text-2xl font-bold ${priceChange !== null && priceChange >= 0 ? "text-green-900" : "text-red-900"}`}> 
              {priceChange !== null ? `${priceChange >= 0 ? "+" : ""}$${Number(priceChange).toFixed(2)}` : "N/A"}
            </div>
            <div className={`text-sm ${percentChange !== null && percentChange >= 0 ? "text-green-700" : "text-red-700"}`}> 
              {percentChange !== null ? `(${percentChange >= 0 ? "+" : ""}${Number(percentChange).toFixed(1)}%)` : "(N/A)"}
            </div>
          </div>

          {/* Confidence */}
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-sm text-purple-600 mb-1 flex items-center justify-center">
              <Clock className="mr-1 h-4 w-4" />
              Confidence
            </div>
            <div className="text-2xl font-bold text-purple-900">
              {confidencePct}
            </div>
            <div className="text-sm text-purple-700">{safeStr(prediction.time_frame)}</div>
          </div>
        </div>

        {/* Reasoning & Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Prediction Summary</h4>
          <p className="text-gray-700">
            <strong>Recommendation:</strong> {safeStr(prediction.recommendation)}<br />
            <strong>Reasoning:</strong> {safeStr(prediction.reasoning)}
          </p>
        </div>
      </CardContent>
    </Card>
  )
} 