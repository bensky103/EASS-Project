import requests

def fetch_fundamentals(symbol: str, api_key: str) -> dict:
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    earnings_url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={api_key}"

    overview = requests.get(overview_url).json()
    earnings = requests.get(earnings_url).json()

    pe_ratio = overview.get("PERatio")
    eps = overview.get("EPS")
    earnings_dates = earnings.get("earningsDate", [])
    next_earnings = earnings_dates[0] if earnings_dates else None

    latest_report = {}
    history = earnings.get("quarterlyEarnings", [])
    if history:
        latest = history[0]
        latest_report = {
            "fiscalDateEnding": latest.get("fiscalDateEnding"),
            "reportedEPS": latest.get("reportedEPS"),
            "estimatedEPS": latest.get("estimatedEPS"),
            "surprise": latest.get("surprise"),
            "surprisePercentage": latest.get("surprisePercentage")
        }

    def safe_float(val, default=0.0):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default
    def safe_int(val, default=0):
        try:
            return int(float(val))
        except (TypeError, ValueError):
            return default

    # Helper to get value from either root or 'Global Quote'
    def get_val(key, default=None):
        if key in overview:
            return overview.get(key, default)
        if 'Global Quote' in overview and key in overview['Global Quote']:
            return overview['Global Quote'].get(key, default)
        return default

    fundamentals = {
        "market_cap": safe_int(get_val("Market Capitalization", 0)),
        "pe_ratio": safe_float(get_val("PERatio", 0.0)),
        "dividend_yield": safe_float(get_val("DividendYield", 0.0)),
        "beta": safe_float(get_val("Beta", 0.0)),
    }
    
    print("\n=== Fundamental Data ===")
    print(f"P/E Ratio: {pe_ratio}")
    print(f"EPS: {eps}")
    print(f"Next Earnings Date: {next_earnings}")
    if latest_report:
        print("\nLatest Earnings Report:")
        print(f"Fiscal Date Ending: {latest_report['fiscalDateEnding']}")
        print(f"Reported EPS: {latest_report['reportedEPS']}")
        print(f"Estimated EPS: {latest_report['estimatedEPS']}")
        print(f"Surprise: {latest_report['surprise']}")
        print(f"Surprise Percentage: {latest_report['surprisePercentage']}%")
    
    return fundamentals

def fetch_news_sentiment(symbol: str, api_key: str) -> dict:
    """Fetch news sentiment data from Alpha Vantage for the given symbol."""
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "Error Message" in data:
            return {"error": data["Error Message"]}
        if "Information" in data:
            return {"error": data["Information"]}
        # Alpha Vantage returns a list of news items with sentiment scores
        feed = data.get("feed", [])
        if not feed:
            return {"sentiment_summary": "No news data available."}
        # Aggregate sentiment
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        headlines = []
        for item in feed:
            sentiment = item.get("overall_sentiment_label", "neutral").lower()
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
            else:
                sentiment_counts["neutral"] += 1
            headlines.append({
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "sentiment": sentiment,
                "relevance_score": item.get("relevance_score", None)
            })
        total = sum(sentiment_counts.values())
        sentiment_score = (
            (sentiment_counts["positive"] - sentiment_counts["negative"]) / total
            if total > 0 else 0.0
        )
        return {
            "sentiment_score": sentiment_score,
            "sentiment_counts": sentiment_counts,
            "headlines": headlines[:5]  # Return up to 5 latest headlines
        }
    except Exception as e:
        return {"error": str(e)} 