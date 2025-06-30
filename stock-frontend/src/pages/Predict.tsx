import { useState, useContext } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, ArrowLeft, Search, CheckCircle, Loader2, Plus } from "lucide-react"
import { Link, useNavigate } from "react-router-dom"
import { AuthContext } from "@/features/auth/context/AuthContext"
import { userService } from "@/services/api"
import { predictService } from "@/services/api"
import PredictionResult from "@/components/ui/PredictionResult"

interface PredictionData {
  ticker: string
  predictedPrice: number
  currentPrice: number
  confidence: number
  direction: "up" | "down"
  timeframe: string
}

export default function PredictPage() {
  const { isAuthenticated, user } = useContext(AuthContext)!
  const [ticker, setTicker] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [prediction, setPrediction] = useState<PredictionData | null>(null)
  const [error, setError] = useState("")
  const [isSuccess, setIsSuccess] = useState(false)
  const [currentPrice, setCurrentPrice] = useState<number | null>(null)
  const [fetchedStockData, setFetchedStockData] = useState<any | null>(null)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!ticker.trim()) return

    setIsLoading(true)
    setError("")
    setPrediction(null)
    setIsSuccess(false)
    setFetchedStockData(null)
    setCurrentPrice(null)

    try {
      // 1. Fetch real technical data from stock_data_fetching service
      let fetchedStockDataToSave = fetchedStockData
      if (!fetchedStockDataToSave) {
        const stockDataRes = await fetch('/fetch/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ symbol: ticker.toUpperCase() }),
        })
        if (!stockDataRes.ok) {
          throw new Error('Failed to fetch technical data')
        }
        fetchedStockDataToSave = await stockDataRes.json()
        // Add ticker and symbol fields if not present
        fetchedStockDataToSave.ticker = ticker.toUpperCase()
        fetchedStockDataToSave.symbol = ticker.toUpperCase()
        // Immediately save the fetched technical data to /user/technical-data
        await fetch('/user/technical-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify(fetchedStockDataToSave),
        })
      }
      // 2. Now call /predict to start the backend prediction process
      const res = await predictService.predict(ticker.toUpperCase())
      const data = res.data
      if (isAuthenticated) {
        try {
          // 3. Save prediction to backend
          const body: any = { ticker: ticker.toUpperCase(), prediction: data };
          await fetch('/user/prediction', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify(body),
          })
          const watchlistRes = await userService.addToWatchlist(ticker.toUpperCase())
          console.log('Add to watchlist response:', watchlistRes)
          // 4. Now fetch the saved prediction for display
          const savedPredictionRes = await userService.getWatchlistTickerData(ticker.toUpperCase())
          setPrediction(savedPredictionRes.data?.prediction || null)
          const fetched = savedPredictionRes.data?.fetchedStockData
          const price = fetched?.technical_indicators?.latest_close ?? null
          setCurrentPrice(price)
        } catch (watchlistErr) {
          console.error('Failed to add to watchlist or save prediction:', watchlistErr)
        }
      } else {
        setPrediction(data)
        setIsSuccess(true)
      }
    } catch (err: any) {
      setError("Failed to generate prediction. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>Please sign in to access stock predictions</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/">
              <Button className="w-full">Return to Home</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4">
      <div className="container mx-auto max-w-4xl py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <Button variant="outline" size="sm" onClick={() => navigate(`/landing/${user?.id || ""}`)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Button>
          <Badge variant="secondary" className="bg-blue-100 text-blue-700">
            Welcome, {user?.username}
          </Badge>
        </div>

        {/* Main Prediction Card */}
        <Card className="shadow-xl mb-8">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-purple-600">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
            <CardTitle className="text-3xl font-bold">AI Stock Prediction</CardTitle>
            <CardDescription className="text-lg">
              Enter a stock ticker symbol to get AI-powered predictions
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Prediction Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="relative">
                <div className="flex gap-3">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <Input
                      type="text"
                      placeholder="Enter stock ticker (e.g., AAPL, TSLA, GOOGL)"
                      value={ticker}
                      onChange={(e) => setTicker(e.target.value.toUpperCase())}
                      className="pl-10 h-12 text-lg font-medium border-2 border-gray-200 focus:border-blue-500 rounded-xl"
                      disabled={isLoading}
                      maxLength={10}
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={isLoading || !ticker.trim()}
                    className="h-12 px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl font-semibold"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Predicting...
                      </>
                    ) : (
                      <>
                        <TrendingUp className="mr-2 h-5 w-5" />
                        Predict
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </form>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-medium">{error}</p>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="text-center py-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                  <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyzing Market Data</h3>
                <p className="text-gray-600">Our AI is processing {ticker} stock data and generating predictions...</p>
              </div>
            )}

            {/* Success Message */}
            {isSuccess && prediction && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  <p className="text-green-800 font-medium">
                    Prediction completed successfully! {ticker.toUpperCase()} has been added to your watchlist.
                  </p>
                </div>
              </div>
            )}

            {/* Prediction Result */}
            {prediction && (
              <div className="mt-8">
                <PredictionResult prediction={prediction} currentPrice={currentPrice} />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        {prediction && (
          <div className="flex gap-4 justify-center mt-8">
            <Button
              variant="outline"
              onClick={() => {
                setTicker("")
                setPrediction(null)
                setIsSuccess(false)
                setError("")
              }}
            >
              Make Another Prediction
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate(`/watchlist/${user?.id || ""}`)}
            >
              <Plus className="mr-2 h-4 w-4" />
              View Watchlist
            </Button>
          </div>
        )}
      </div>
    </div>
  )
} 