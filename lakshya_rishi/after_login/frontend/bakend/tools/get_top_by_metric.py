import yfinance as yf
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# List of stocks
symbols = [
    'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
    'BAJFINANCE.NS', 'BAJAJFINSV.NS',
    'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS',
    'RELIANCE.NS', 'NTPC.NS', 'IOC.NS',
    'TATAMOTORS.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS',
    'SUNPHARMA.NS', 'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS',
    'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS',
    'ULTRACEMCO.NS', 'GRASIM.NS', 'BHARTIARTL.NS', 'DMART.NS',
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
    'ADBE', 'INTC', 'AMD', 'CRM', 'PYPL', 'UBER', 'SHOP', 'SNOW',
    'PLTR', 'BABA', 'JNJ', 'PFE', 'DIS'
]

def fetch_stock_metric(sym, metric, start_date, end_date):
    try:
        stock = yf.Ticker(sym)
        info = stock.info
        if not info or "shortName" not in info:
            return None

        if metric == "return":
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty or len(hist) < 2:
                return None
            old_price = hist["Close"].iloc[0]
            new_price = hist["Close"].iloc[-1]
            value = ((new_price - old_price) / old_price) * 100
            return {"symbol": sym, "value": round(value, 2)}

        elif metric == "roe":
            value = info.get("returnOnEquity")
            if value is not None:
                return {"symbol": sym, "value": round(value * 100, 2)}

        elif metric == "eps":
            value = info.get("trailingEps")
            if value is not None:
                return {"symbol": sym, "value": round(value, 2)}

        elif metric == "pe_ratio":
            value = info.get("trailingPE")
            if value is not None:
                return {"symbol": sym, "value": round(value, 2)}

        return None
    except:
        return None

def get_top_by_metric(metric="return", period_days=7, top_n=5, reverse=True):
    metric = metric.lower()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=period_days + 1)).strftime("%Y-%m-%d")

    result = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(fetch_stock_metric, sym, metric, start_date, end_date) for sym in symbols]
        for future in as_completed(futures):
            data = future.result()
            if data:
                result.append(data)

    if not result:
        return f"⚠️ No data found for metric '{metric}'."

    sorted_result = sorted(result, key=lambda x: x["value"], reverse=reverse)

    label_map = {
        "return": f"{period_days}-day Return (%)",
        "roe": "Return on Equity (%)",
        "eps": "Earnings per Share (EPS)",
        "pe_ratio": "P/E Ratio"
    }

    response = f"📊 Top {top_n} stocks by {label_map.get(metric, metric)}:\n"
    for i, item in enumerate(sorted_result[:top_n], start=1):
        unit = "%" if metric in ["return", "roe"] else ""
        response += f"{i}. {item['symbol']} – {item['value']}{unit}\n"

    # Add date and time
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    response += f"\n🕒 Data as of {now}"
    return response

def get_top_by_metric_wrapper(user_input: str) -> str:
    metric = "return"
    period_days = 7
    top_n = 5
    reverse = True

    try:
        cleaned = user_input.replace(" ", "").lower()

        # Keyword-based detection
        if "roe" in cleaned or "profit" in cleaned or "profitable" in cleaned:
            metric = "roe"
        elif "eps" in cleaned or "earning" in cleaned:
            metric = "eps"
        elif "pe" in cleaned and "ratio" in cleaned:
            metric = "pe_ratio"
            reverse = False
        elif "return" in cleaned or "topstock" in cleaned or "topstocks" in cleaned \
             or "trending" in cleaned or "performing" in cleaned or "best" in cleaned:
            metric = "return"

        # Manual override: metric=roe,top_n=5,period_days=10,reverse=true
        for part in cleaned.split(","):
            if "metric=" in part:
                metric = part.split("=")[1].strip("'\"")
            elif "top_n=" in part:
                top_n = int(part.split("=")[1].strip("'\""))
            elif "reverse=" in part:
                reverse = part.split("=")[1].strip("'\"") == "true"
            elif "period_days=" in part:
                period_days = int(part.split("=")[1].strip("'\""))

        return get_top_by_metric(metric=metric, period_days=period_days, top_n=top_n, reverse=reverse)

    except Exception as e:
        return f"❌ Error parsing input: {str(e)}"
