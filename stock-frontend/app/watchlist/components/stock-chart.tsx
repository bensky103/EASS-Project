import { Line, LineChart, ResponsiveContainer, YAxis } from "recharts"

interface ChartData {
  time: number
  price: number
}

interface StockChartProps {
  data: ChartData[]
  isPositive: boolean
  ticker: string
}

export default function StockChart({ data, isPositive, ticker }: StockChartProps) {
  // Transform data for recharts
  const chartData = data.map((point, index) => ({
    index,
    price: point.price,
  }))

  const minPrice = Math.min(...data.map((d) => d.price))
  const maxPrice = Math.max(...data.map((d) => d.price))
  const padding = (maxPrice - minPrice) * 0.1

  return (
    <div className="w-full h-full relative">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <defs>
            <linearGradient id={`gradient-${ticker}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.3} />
              <stop offset="100%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <YAxis domain={[minPrice - padding, maxPrice + padding]} hide />
          <Line
            type="monotone"
            dataKey="price"
            stroke={isPositive ? "#10b981" : "#ef4444"}
            strokeWidth={2}
            dot={false}
            fill={`url(#gradient-${ticker})`}
            fillOpacity={1}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* TradingView-style branding */}
      <div className="absolute bottom-1 right-2 text-xs text-gray-400 font-medium">StockAI</div>
    </div>
  )
}
