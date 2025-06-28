"use client"

import { ResponsiveContainer, XAxis, YAxis, Tooltip, Area, AreaChart } from "recharts"

interface ChartData {
  time: number
  price: number
}

interface FullScreenChartProps {
  data: ChartData[]
  ticker: string
  isPositive: boolean
}

export default function FullScreenChart({ data, ticker, isPositive }: FullScreenChartProps) {
  // Fallback to empty array if data is undefined or not an array
  const safeData = Array.isArray(data) ? data : [];

  // Transform data for recharts
  const chartData = safeData.map((point, index) => ({
    index,
    price: point.price,
    // Format date as MM/DD or YYYY-MM-DD
    date: (() => {
      const d = new Date(point.time);
      // If the year is not this year, show year
      const now = new Date();
      if (d.getFullYear() !== now.getFullYear()) {
        return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
      }
      return `${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')}`;
    })(),
  }))

  const minPrice = safeData.length > 0 ? Math.min(...safeData.map((d) => d.price)) : 0;
  const maxPrice = safeData.length > 0 ? Math.max(...safeData.map((d) => d.price)) : 0;
  const padding = (maxPrice - minPrice) * 0.05;

  return (
    <div className="w-full h-full relative bg-white">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <defs>
            <linearGradient id={`fullGradient-${ticker}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.4} />
              <stop offset="50%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.2} />
              <stop offset="100%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#6b7280" }}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[minPrice - padding, maxPrice + padding]}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#6b7280" }}
            tickFormatter={(value) => `$${value.toFixed(0)}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, "Price"]}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke={isPositive ? "#10b981" : "#ef4444"}
            strokeWidth={3}
            fill={`url(#fullGradient-${ticker})`}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
} 