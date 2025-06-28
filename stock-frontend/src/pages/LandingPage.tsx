import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Brain, Shield, Zap, BarChart3, Users, Star, ArrowRight, User as UserIcon } from "lucide-react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { useContext, useState } from "react"
import { AuthContext } from "@/features/auth/context/AuthContext"
import { UserDropdown } from "@/components/user-dropdown"

export default function LandingPage() {
  const auth = useContext(AuthContext)
  const user = auth?.user
  const navigate = useNavigate()
  const { userId } = useParams()
  const isLoggedIn = user && userId && user.id === userId

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">StockAI Pro</span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-gray-600 hover:text-gray-900">Features</a>
            <a href="#reviews" className="text-gray-600 hover:text-gray-900">Reviews</a>
            <a href="#about" className="text-gray-600 hover:text-gray-900">About</a>
            {isLoggedIn ? (
              <UserDropdown user={user} onLogout={auth.logout} />
            ) : (
              <>
                <button className="btn btn-outline text-sm px-4 py-2 rounded border" onClick={() => navigate("/login")}>Sign In</button>
                <button className="btn text-sm px-4 py-2 rounded bg-blue-600 text-white ml-2" onClick={() => navigate("/register")}>Get Started</button>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-100">
            <Brain className="w-3 h-3 mr-1" />
            Powered by Ollama AI
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Predict Stock Movements with
            <span className="text-blue-600 block">AI Precision</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Harness the power of advanced Ollama AI models to analyze market trends, predict stock movements, and make
            informed investment decisions with confidence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
            {isLoggedIn ? null : (
              <>
                <button className="btn text-lg px-8 py-3 bg-blue-600 text-white rounded flex items-center justify-center" onClick={() => navigate("/register")}> 
                  <span className="flex items-center">Start Free Trial <ArrowRight className="ml-2 h-5 w-5" /></span>
                </button>
                <button className="btn text-lg px-8 py-3 border rounded" onClick={() => navigate("/login")}>Sign In</button>
              </>
            )}
          </div>
          {!isLoggedIn && (
            <p className="text-sm text-gray-500 mt-4">No credit card required • 14-day free trial • Cancel anytime</p>
          )}
        </div>
      </section>
      {/* Make Prediction Button - Only visible when authenticated */}
      {auth?.isAuthenticated && (
        <div className="mb-16 flex justify-center">
          <div className="relative w-full max-w-4xl">
            {/* Solid filled box */}
            <div className="bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-3xl shadow-2xl p-12 md:p-16 lg:p-20 transform hover:scale-[1.02] transition-all duration-300">
              <Link to="/predict">
                <Button
                  size="lg"
                  className="bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white font-bold px-12 py-6 md:px-16 md:py-8 text-xl md:text-2xl lg:text-3xl rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border-2 border-white/30 w-full"
                >
                  <TrendingUp className="mr-3 h-6 w-6 md:h-8 md:w-8" />
                  GENERATE AI POWERED PREDICTION
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}
      
      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Advanced AI-Powered Features</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our Ollama AI integration provides cutting-edge analysis and predictions to give you the edge in stock
              trading.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <Brain className="h-12 w-12 text-blue-600 mb-4" />
                <CardTitle>AI-Powered Analysis</CardTitle>
                <CardDescription>
                  Advanced Ollama models analyze thousands of data points to identify patterns and trends
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <BarChart3 className="h-12 w-12 text-green-600 mb-4" />
                <CardTitle>Real-Time Predictions</CardTitle>
                <CardDescription>
                  Get instant stock movement predictions with confidence scores and risk assessments
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <Shield className="h-12 w-12 text-purple-600 mb-4" />
                <CardTitle>Risk Management</CardTitle>
                <CardDescription>
                  Built-in risk analysis helps you make safer investment decisions with AI guidance
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <Zap className="h-12 w-12 text-yellow-600 mb-4" />
                <CardTitle>Lightning Fast</CardTitle>
                <CardDescription>
                  Process market data and generate predictions in milliseconds using optimized AI models
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <TrendingUp className="h-12 w-12 text-red-600 mb-4" />
                <CardTitle>Market Insights</CardTitle>
                <CardDescription>
                  Deep market analysis with sentiment tracking and news impact assessment
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <Users className="h-12 w-12 text-indigo-600 mb-4" />
                <CardTitle>Portfolio Optimization</CardTitle>
                <CardDescription>
                  AI-driven portfolio recommendations to maximize returns and minimize risk
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Reviews Section */}
      <section id="reviews" className="py-20 px-4 bg-blue-600 text-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Trusted by Professional Traders</h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-4">
                  "StockAI Pro's Ollama integration has revolutionized my trading strategy. The accuracy is incredible
                  and has significantly improved my returns."
                </p>
                <div className="font-semibold">Sarah Chen</div>
                <div className="text-sm text-gray-500">Portfolio Manager</div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-4">
                  "The AI predictions are spot-on. I've been using it for 6 months and my success rate has increased by
                  40%."
                </p>
                <div className="font-semibold">Michael Rodriguez</div>
                <div className="text-sm text-gray-500">Day Trader</div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-4">
                  "Finally, an AI tool that actually works. The Ollama integration provides insights I never could have
                  found manually."
                </p>
                <div className="font-semibold">Emma Thompson</div>
                <div className="text-sm text-gray-500">Investment Analyst</div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto text-center max-w-4xl">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">About StockAI Pro</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            [Placeholder] StockAI Pro is an advanced AI-powered platform for stock prediction and analytics. More info coming soon.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Transform Your Trading?</h2>
          <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
            Join thousands of successful traders who trust StockAI Pro's Ollama-powered predictions for their investment
            decisions.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="text-lg px-8 py-3" asChild>
              <Link to="/watchlist">Start Free Trial</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <TrendingUp className="h-6 w-6 text-blue-400" />
                <span className="text-lg font-bold">StockAI Pro</span>
              </div>
              <p className="text-gray-400">Advanced AI-powered stock prediction platform using Ollama technology.</p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="#" className="hover:text-white">
                    Features
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    API
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Documentation
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="#" className="hover:text-white">
                    About
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Careers
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Contact
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="#" className="hover:text-white">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-white">
                    Status
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 StockAI Pro. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
