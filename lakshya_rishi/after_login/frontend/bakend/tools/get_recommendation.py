import os
import sys
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.get_sentiment import get_sentiment
from llm_config import llm

# ✅ Predefined U.S. stock universe
US_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
    'ADBE', 'INTC', 'AMD', 'CRM', 'PYPL', 'UBER', 'SHOP', 'SNOW',
    'PLTR', 'BABA', 'JNJ', 'PFE', 'DIS'
]

def fetch_change(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        price = info.get("regularMarketPrice")
        change = info.get("regularMarketChangePercent")
        if price is not None and change is not None:
            return {"symbol": symbol, "change": change}
    except:
        pass
    return None

def get_recommendation(_: str = "") -> str:
    try:
        print("🔍 Step 1: Fetching top 5 trending U.S. stocks based on % change...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_change, US_STOCKS))

        # Remove None results and sort by highest % change
        valid = [r for r in results if r is not None]
        trending = sorted(valid, key=lambda x: x["change"], reverse=True)[:5]
        tickers = [x["symbol"] for x in trending]

        if not tickers:
            return "⚠️ No valid U.S. stocks found."

        print(f"✅ Trending candidates: {tickers}")
        print("📰 Step 2: Fetching sentiment in parallel...")

        sentiments = []

        def fetch_sentiment(stock):
            return stock, get_sentiment(stock)

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_sentiment, tickers))

        for stock, sentiment in results:
            if isinstance(sentiment, dict):
                status = sentiment.get("sentiment", "").strip().lower()
                reason = sentiment.get("reason", "")
                if status and status != "neutral":
                    sentiments.append({
                        "stock": stock,
                        "sentiment": status.capitalize(),
                        "reason": reason
                    })

        if not sentiments:
            print("⚠️ No strong sentiment found. Using neutral fallback.")
            sentiments = [
                {"stock": stock, "sentiment": "Neutral", "reason": "No strong sentiment available"}
                for stock in tickers
            ]

        sorted_candidates = sorted(
            sentiments, key=lambda x: {"positive": 0, "neutral": 1, "negative": 2}.get(x["sentiment"].lower(), 3)
        )[:5]

        context = ""
        for s in sorted_candidates:
            context += f"\nStock: {s['stock']}\nSentiment: {s['sentiment']} - {s['reason']}\n"

        print("🧠 Asking LLM for recommendation...")
        prompt = f"""
        Based on the following U.S. stocks and their news sentiment, recommend the top 2-3 stocks to buy today.
        Justify your recommendation briefly.

        {context}

        Give answer in this format:
        Recommendation:
        - Stock 1: reason
        - Stock 2: reason
        """

        response = llm.invoke(prompt)
        print("✅ LLM responded.")
        return response.content.strip()

    except Exception as e:
        return f"❌ Error generating stock recommendation: {e}"

if __name__ == "__main__":
    print(get_recommendation())
