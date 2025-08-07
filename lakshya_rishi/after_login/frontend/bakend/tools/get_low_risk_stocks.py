import yfinance as yf
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🌍 Global Stocks (U.S.)
GLOBAL_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "ADBE",
    "NFLX", "CRM", "INTC", "AMD", "JNJ", "PFE", "DIS", "BABA", "UBER",
    "PYPL", "SHOP", "PLTR"
]

# 🇮🇳 Reliable Indian Stocks (handpicked)
INDIAN_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ITC.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "SBIN.NS", "BAJFINANCE.NS", "HCLTECH.NS",
    "LT.NS", "COALINDIA.NS", "SUNPHARMA.NS", "DIVISLAB.NS",
    "MARUTI.NS", "TATAMOTORS.NS", "IRCTC.NS"
]

# Worker function
def fetch_stock_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        beta = info.get("beta")
        roe = info.get("returnOnEquity")
        eps = info.get("trailingEps")

        if beta is not None and beta < 1 and roe and roe > 0.1 and eps and eps > 0:
            return {
                "Ticker": ticker,
                "Beta": round(beta, 2),
                "ROE": round(roe * 100, 2),
                "EPS": round(eps, 2)
            }
    except Exception as e:
        print(f"⚠️ Skipping {ticker}: {e}")
    return None

def get_low_risk_stock(input_str: str = "5") -> str:
    input_str = input_str.lower()

    # Filter stock list based on region keyword
    if "indian" in input_str:
        stock_list = INDIAN_STOCKS
    elif "us" in input_str or "global" in input_str:
        stock_list = GLOBAL_STOCKS
    else:
        stock_list = GLOBAL_STOCKS + INDIAN_STOCKS

    # Extract number from input
    try:
        top_n = int("".join([c for c in input_str if c.isdigit()])) or 5
    except:
        top_n = 5

    result = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_stock_info, ticker): ticker for ticker in stock_list}
        for future in as_completed(futures):
            stock_data = future.result()
            if stock_data:
                result.append(stock_data)

    if not result:
        return "⚠️ Could not find any low-risk stocks."

    df = pd.DataFrame(result).sort_values(by="Beta")
    response = "🛡️ **Top Low-Risk Stocks (Beta < 1, ROE > 10%, EPS > 0):**\n\n"
    for _, row in df.head(top_n).iterrows():
        response += (
            f"🔹 {row['Ticker']} → Beta: {row['Beta']} | "
            f"ROE: {row['ROE']}% | EPS: {row['EPS']}\n"
        )

    return response.strip()
