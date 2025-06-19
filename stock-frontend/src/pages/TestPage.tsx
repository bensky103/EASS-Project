import { Button } from "@/components/ui/button"

export default function TestPage() {
  return (
    <div className="min-h-screen bg-blue-500 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Tailwind Test</h1>
        <p className="text-gray-600 mb-4">If you can see this styled, Tailwind is working!</p>
        <Button className="bg-blue-600 text-white px-4 py-2 rounded">
          Test Button
        </Button>
      </div>
    </div>
  )
}
