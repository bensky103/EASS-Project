import { Line, LineChart, ResponsiveContainer, YAxis, XAxis, CartesianGrid, Tooltip } from "recharts"

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
  const minPrice = Math.min(...data.map((d) => d.price))
  const maxPrice = Math.max(...data.map((d) => d.price))
  const padding = (maxPrice - minPrice) * 0.1

  // Format price as dollars
  const formatPrice = (price: number) => `$${price.toFixed(2)}`
  // Format date as MM/DD
  const formatDate = (unixTime: number) => {
    const d = new Date(unixTime)
    return `${d.getMonth() + 1}/${d.getDate()}`
  }

  // Convert data to use date strings for X axis
  const chartData = data.map(d => ({ ...d, date: formatDate(d.time) }))

  return (
    <div className="w-full h-full pl-4 pr-2 relative bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 20 }}>
          <defs>
            <linearGradient id={`gradient-${ticker}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.3} />
              <stop offset="100%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
          <YAxis 
            domain={[minPrice - padding, maxPrice + padding]} 
            tick={{ fontSize: 11, fill: '#888' }} 
            width={40}
            tickFormatter={formatPrice}
            axisLine={false}
            tickLine={false}
          />
          <XAxis
            dataKey="date"
            type="category"
            tick={{ fontSize: 11, fill: '#888' }}
            height={24}
            label={{ value: 'Time', position: 'insideBottom', offset: 0, fontSize: 12, fill: '#888' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip 
            formatter={(value, name) => name === 'price' ? formatPrice(Number(value)) : value}
            labelFormatter={label => label}
            contentStyle={{ borderRadius: 8, fontSize: 13 }}
          />
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