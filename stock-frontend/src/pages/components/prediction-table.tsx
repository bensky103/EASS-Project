"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { PricePrediction } from "../types/analysis"

interface PredictionTableProps {
  predictions: PricePrediction[]
  currentPrice: number
}

export default function PredictionTable({ predictions, currentPrice }: PredictionTableProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    })
  }

  const getPriceChange = (predictedPrice: number) => {
    const change = predictedPrice - currentPrice
    const changePercent = (change / currentPrice) * 100
    return { change, changePercent }
  }

  return (
    <div className="bg-white rounded-lg border overflow-hidden">
      <div className="p-4 bg-gray-50 border-b">
        <h4 className="font-semibold text-gray-900">Price Forecast</h4>
        <p className="text-sm text-gray-600">AI-generated price forecasts</p>
      </div>

      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Predicted Price</TableHead>
              <TableHead>Change</TableHead>
              <TableHead>Change %</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {predictions.map((prediction, index) => {
              const { change, changePercent } = getPriceChange(prediction.predictedPrice)
              return (
                <TableRow key={index}>
                  <TableCell className="font-medium">{formatDate(prediction.date)}</TableCell>
                  <TableCell className="font-semibold">${prediction.predictedPrice.toFixed(2)}</TableCell>
                  <TableCell className={change >= 0 ? "text-green-600" : "text-red-600"}>
                    {change >= 0 ? "+" : ""}
                    {change.toFixed(2)}
                  </TableCell>
                  <TableCell className={changePercent >= 0 ? "text-green-600" : "text-red-600"}>
                    {changePercent >= 0 ? "+" : ""}
                    {changePercent.toFixed(1)}%
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  )
} 