import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
import yfinance as yf

# Add parent dir to import llm_config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env
load_dotenv()


def resolve_ticker_with_llm(user_input: str) -> str:
    """
    Uses LLM to resolve user input to a valid U.S. stock ticker.
    """
    from llm_config import llm

    prompt = f"""
You are a financial assistant. The user typed: "{user_input}".

Your task is to return ONLY the official **stock ticker** for a **U.S.-listed company** matching this input.

❌ Do NOT return:
- Indian stocks (e.g., TCS.NS, RELIANCE.NS)
- Stocks listed outside the U.S. (e.g., TATAY, BABA.HK)
- Any ticker ending in `.NS` or not on the U.S. exchanges

✅ Return ONLY a valid U.S. stock ticker (like AAPL, MSFT, GOOGL).
If you are not sure, return "UNKNOWN".
No extra text, only the ticker.
"""
    result = llm.invoke(prompt).content.strip().upper()
    return result


def is_valid_ticker(ticker: str) -> bool:
    """
    Verifies if the ticker exists and is valid on Yahoo Finance.
    """
    if ticker.endswith(".NS"):
        return False  # explicitly reject Indian tickers

    try:
        info = yf.Ticker(ticker).info
        return "shortName" in info and info.get("regularMarketPrice") is not None
    except:
        return False


def get_finnhub_news(symbol: str) -> str:
    """
    Fetches recent news for the given ticker using Finnhub.
    """
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return "❌ FINNHUB_API_KEY not set in your .env file."

    today = datetime.now().date()
    start = today - timedelta(days=3)

    url = "https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": symbol,
        "from": start.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d"),
        "token": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return f"⚠️ No recent news found for {symbol}."

        result = f"📰 Recent News for {symbol}:\n\n"
        for item in data[:5]:
            date = datetime.fromtimestamp(item["datetime"]).strftime("%Y-%m-%d")
            source = item.get("source", "Unknown")
            headline = item.get("headline", "No headline")
            result += f"📅 {date} | 🏢 {source}\n🔹 {headline}\n\n"
        return result.strip()

    except Exception as e:
        return f"❌ Error fetching news: {str(e)}"


def get_sentiment(user_input: str) -> str:
    """
    Resolves ticker, fetches news, and analyzes sentiment.
    """
    symbol = resolve_ticker_with_llm(user_input)
    if symbol == "UNKNOWN" or not is_valid_ticker(symbol):
        return (
            f"❌ Could not identify a valid U.S. stock ticker for '{user_input}'.\n\n"
            f"This may be due to a typo or because '{user_input}' is an Indian or foreign company.\n"
            f"Currently, we provide news and sentiment analysis **only for U.S.-listed companies**.\n\n"
            f"📢 Interested in Indian stock insights? Support our project to bring Indian market coverage soon!"
        )


    news = get_finnhub_news(symbol)

    if news.startswith("❌") or news.startswith("⚠️"):
        return news

    from llm_config import llm

    prompt = (
        "Analyze the sentiment of the following company news headlines. "
        "Respond with either Positive, Negative, or Neutral and give a brief reason.\n\n"
        f"{news}"
    )

    analysis = llm.invoke(prompt).content.strip()

    return f"{news}\n\n🔍 Sentiment Analysis:\n{analysis}"


if __name__ == "__main__":
    query = input("Enter a company name (e.g. Microsoft, Adobe, TCS): ")
    print(get_sentiment(query))






# import os
# import requests
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
# from rapidfuzz import process 
# import sys

# # Add parent dir to import llm_config
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# # Load environment variables from .env
# load_dotenv()

# # ✅ Known companies and their tickers (U.S. + India)
# company_map = {
#     "apple": "AAPL", "meta": "META", "google": "GOOGL", "alphabet": "GOOGL", "amazon": "AMZN",
#     "microsoft": "MSFT", "tesla": "TSLA", "nvidia": "NVDA", "adobe": "ADBE", "netflix": "NFLX",
#     "intel": "INTC", "amd": "AMD", "paypal": "PYPL", "uber": "UBER", "shopify": "SHOP",
#     "snowflake": "SNOW", "palantir": "PLTR", "alibaba": "BABA", "disney": "DIS",
#     "pfizer": "PFE", "johnson": "JNJ",

#     # Indian stocks (unsupported in this tool)
#     "tcs": "TCS.NS", "reliance": "RELIANCE.NS", "infosys": "INFY.NS", "hdfc": "HDFCBANK.NS",
#     "icici": "ICICIBANK.NS", "wipro": "WIPRO.NS", "itc": "ITC.NS"
# }


# def resolve_company_name(user_input: str) -> str:
#     """
#     Fuzzy resolves user input to a company ticker using known names.
#     """
#     cleaned = user_input.strip().lower()
#     if cleaned in company_map:
#         return company_map[cleaned]

#     match, score, _ = process.extractOne(cleaned, company_map.keys())
#     if score >= 80:
#         return company_map[match]

#     return user_input.upper()  # Fallback if it's already a valid ticker


# def get_finnhub_news(symbol: str) -> str:
#     """
#     Fetches the latest 3-day news headlines for a given stock symbol.
#     """
#     api_key = os.getenv("FINNHUB_API_KEY")
#     if not api_key:
#         return "❌ FINNHUB_API_KEY not set in your .env file."

#     today = datetime.now().date()
#     start = today - timedelta(days=3)

#     url = "https://finnhub.io/api/v1/company-news"
#     params = {
#         "symbol": symbol,
#         "from": start.strftime("%Y-%m-%d"),
#         "to": today.strftime("%Y-%m-%d"),
#         "token": api_key
#     }

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()

#         if not data:
#             return f"⚠️ No recent news found for {symbol}."

#         result = f"📰 Recent News for {symbol}:\n\n"
#         for item in data[:5]:
#             date = datetime.fromtimestamp(item["datetime"]).strftime("%Y-%m-%d")
#             source = item.get("source", "Unknown")
#             headline = item.get("headline", "No headline")
#             result += f"📅 {date} | 🏢 {source}\n🔹 {headline}\n\n"
#         return result.strip()

#     except Exception as e:
#         return f"❌ Error fetching news: {str(e)}"


# def get_sentiment(user_input: str) -> str:
#     """
#     Returns the latest company news and sentiment analysis in raw text format (no HTML).
#     """
#     symbol = resolve_company_name(user_input)

#     # Reject Indian stocks
#     if symbol.endswith(".NS"):
#         return f"❌ News data for Indian stock '{symbol}' is not available."

#     news = get_finnhub_news(symbol)

#     # If API failed or no data
#     if news.startswith("❌") or news.startswith("⚠️"):
#         return news

#     from llm_config import llm

#     prompt = (
#         "Analyze the sentiment of the following company news headlines. "
#         "Respond with either Positive, Negative, or Neutral and give a brief reason.\n\n"
#         f"{news}"
#     )

#     analysis = llm.invoke(prompt).content

#     # Final plain-text output (leave formatting to UI)
#     return f"{news}\n\n🔍 Sentiment Analysis:\n{analysis}"


# # ✅ CLI test
# if __name__ == "__main__":
#     query = input("Enter a company name (e.g. Microsoft, Adobe, TCS): ")
#     print(get_sentiment(query))
