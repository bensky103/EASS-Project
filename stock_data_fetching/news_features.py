import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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

def fetch_advanced_news_sentiment(symbol: str, api_key: str) -> dict:
    """
    Fetches advanced news sentiment features over the last 7 days.
    - Average sentiment score
    - Headline count per day
    - Sentiment momentum (slope of sentiment score)
    """
    # Fetch up to 1000 latest news articles
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&limit=1000&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "feed" not in data or not data["feed"]:
            return {
                "avg_sentiment_7d": np.nan,
                "headline_counts_7d": {},
                "sentiment_momentum": np.nan
            }

        feed = data["feed"]
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(feed)
        
        # Convert time_published to datetime objects
        df['time_published'] = pd.to_datetime(df['time_published'], format='%Y%m%dT%H%M%S')
        
        # Filter for the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        df_7d = df[df['time_published'] >= seven_days_ago].copy()

        if df_7d.empty:
            return {
                "avg_sentiment_7d": np.nan,
                "headline_counts_7d": {},
                "sentiment_momentum": np.nan
            }
            
        # Calculate Average Sentiment Score
        # Find the relevance score for the ticker
        def get_ticker_sentiment(row):
            for ticker_sentiment in row['ticker_sentiment']:
                if ticker_sentiment['ticker'] == symbol:
                    return float(ticker_sentiment['relevance_score']), float(ticker_sentiment['ticker_sentiment_score'])
            return 0.0, 0.0

        sentiments = [get_ticker_sentiment(row) for _, row in df_7d.iterrows()]
        df_7d[['relevance_score', 'sentiment_score']] = sentiments
        
        # Weigh sentiment by relevance
        weighted_sentiment = (df_7d['sentiment_score'] * df_7d['relevance_score']).sum()
        total_relevance = df_7d['relevance_score'].sum()
        avg_sentiment = weighted_sentiment / total_relevance if total_relevance > 0 else 0.0

        # Headline count per day
        df_7d['date'] = df_7d['time_published'].dt.date
        headline_counts = df_7d['date'].value_counts().to_dict()
        headline_counts_serializable = {d.isoformat(): v for d, v in headline_counts.items()}

        # Sentiment Momentum (slope of sentiment over time)
        df_7d = df_7d.sort_values(by='time_published').reset_index(drop=True)
        if len(df_7d) > 1:
            # Use numeric representation of time for regression
            df_7d['time_numeric'] = (df_7d['time_published'] - df_7d['time_published'].min()).dt.total_seconds()
            
            # Use weighted sentiment for momentum calculation
            df_7d['weighted_sentiment'] = df_7d['sentiment_score'] * df_7d['relevance_score']

            # Simple linear regression (slope)
            slope, _ = np.polyfit(df_7d['time_numeric'], df_7d['weighted_sentiment'], 1)
        else:
            slope = 0.0

        return {
            "avg_sentiment_7d": avg_sentiment,
            "headline_counts_7d": headline_counts_serializable,
            "sentiment_momentum": round(slope, 8)
        }

    except Exception as e:
        print(f"Error fetching advanced news sentiment for {symbol}: {e}")
        return {
            "avg_sentiment_7d": np.nan,
            "headline_counts_7d": {},
            "sentiment_momentum": np.nan
        } 