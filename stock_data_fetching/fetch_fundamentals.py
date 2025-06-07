import requests
import numpy as np

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

def fetch_extended_fundamentals(symbol: str, api_key: str) -> dict:
    """
    Fetches extended fundamental data from OVERVIEW, INCOME_STATEMENT, and BALANCE_SHEET.
    """
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    income_url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}"
    balance_sheet_url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={api_key}"

    try:
        overview_data = requests.get(overview_url).json()
        income_data = requests.get(income_url).json()
        balance_sheet_data = requests.get(balance_sheet_url).json()

        def to_float(value):
            if value is None or value == "None":
                return np.nan
            try:
                return float(value)
            except (ValueError, TypeError):
                return np.nan

        # From OVERVIEW
        eps = to_float(overview_data.get("EPS"))
        roe = to_float(overview_data.get("ReturnOnEquityTTM"))
        operating_margin_ttm = to_float(overview_data.get("OperatingMarginTTM"))

        # From INCOME_STATEMENT for Revenue Growth
        annual_reports = income_data.get("annualReports", [])
        revenue_growth = np.nan
        if len(annual_reports) >= 2:
            latest_revenue = to_float(annual_reports[0].get("totalRevenue"))
            previous_revenue = to_float(annual_reports[1].get("totalRevenue"))
            if latest_revenue and previous_revenue and previous_revenue > 0:
                revenue_growth = (latest_revenue - previous_revenue) / previous_revenue

        # From BALANCE_SHEET for Debt/Equity
        annual_balance_sheets = balance_sheet_data.get("annualReports", [])
        debt_equity_ratio = np.nan
        if annual_balance_sheets:
            latest_sheet = annual_balance_sheets[0]
            total_liabilities = to_float(latest_sheet.get("totalLiabilities"))
            total_shareholder_equity = to_float(latest_sheet.get("totalShareholderEquity"))
            if total_shareholder_equity and total_shareholder_equity > 0:
                debt_equity_ratio = total_liabilities / total_shareholder_equity
        
        # Free Cash Flow is not available from these endpoints.

        return {
            "eps": eps,
            "revenue_growth_yoy": revenue_growth,
            "roe": roe,
            "debt_equity_ratio": debt_equity_ratio,
            "operating_margin_ttm": operating_margin_ttm
        }

    except Exception as e:
        print(f"Error fetching extended fundamentals for {symbol}: {e}")
        return {
            "eps": np.nan,
            "revenue_growth_yoy": np.nan,
            "roe": np.nan,
            "debt_equity_ratio": np.nan,
            "operating_margin_ttm": np.nan
        } 