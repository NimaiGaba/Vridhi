import yfinance as yf
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor

INDIAN_STOCKS = [
    'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
    'BAJFINANCE.NS', 'BAJAJFINSV.NS',
    'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS',
    'RELIANCE.NS', 'NTPC.NS', 'IOC.NS',
    'TATAMOTORS.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS',
    'SUNPHARMA.NS', 'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS',
    'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS',
    'ULTRACEMCO.NS', 'GRASIM.NS', 'BHARTIARTL.NS', 'DMART.NS'
]

US_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
    'ADBE', 'INTC', 'AMD', 'CRM', 'PYPL', 'UBER', 'SHOP', 'SNOW',
    'PLTR', 'BABA', 'JNJ', 'PFE', 'DIS'
]

def fetch_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "symbol": symbol,
            "name": info.get("shortName", symbol),
            "price": info.get("regularMarketPrice"),
            "change": info.get("regularMarketChangePercent")
        }
    except:
        return None

def get_trending_stocks(prompt: str = ""):
    start_time = time.time()

    all_symbols = INDIAN_STOCKS + US_STOCKS
    result = []

    with ThreadPoolExecutor(max_workers=15) as executor:
        responses = list(executor.map(fetch_stock_info, all_symbols))

    for stock in responses:
        if stock and stock["price"] is not None and stock["change"] is not None:
            result.append(stock)

    # Separate and sort
    indian = sorted([s for s in result if ".NS" in s["symbol"]], key=lambda x: x["change"], reverse=True)
    us = sorted([s for s in result if ".NS" not in s["symbol"]], key=lambda x: x["change"], reverse=True)

    # Handle prompt
    prompt = prompt.lower()
    top_n_india = 3
    top_n_us = 2
    show_india = show_us = False

    if "top" in prompt:
        if "india" in prompt:
            show_india = True
            try: top_n_india = int(prompt.split("top")[1].split()[0])
            except: top_n_india = 5
        elif "us" in prompt or "usa" in prompt or "america" in prompt:
            show_us = True
            try: top_n_us = int(prompt.split("top")[1].split()[0])
            except: top_n_us = 5
        elif "global" in prompt:
            show_india = show_us = True
        elif "stock" in prompt and "india" not in prompt and "us" not in prompt:
            show_india = show_us = True
            top_n_india = top_n_us = 1
    else:
        show_india = show_us = True

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"📊 Trending Stocks Today (as of {now}):\n\n"

    if show_india:
        output += f"🇮🇳 Top {top_n_india} Indian Stocks:\n"
        for i, stock in enumerate(indian[:top_n_india], 1):
            emoji = "📈" if stock["change"] > 0 else "📉"
            output += f"{i}. {emoji} {stock['name']} – ₹{stock['price']} ({round(stock['change'], 2)}%)\n"
        output += "\n"

    if show_us:
        output += f"🇺🇸 Top {top_n_us} U.S. Stocks:\n"
        for i, stock in enumerate(us[:top_n_us], 1):
            emoji = "📈" if stock["change"] > 0 else "📉"
            output += f"{i}. {emoji} {stock['name']} – ${stock['price']} ({round(stock['change'], 2)}%)\n"

    # runtime = round(time.time() - start_time, 2)
    # output += f"\n⏱️ Fetched in {runtime} seconds"
    return output.strip()

# Test from terminal
if __name__ == "__main__":
    prompt = input("Enter prompt (e.g., 'top 5 india', 'top 10 usa', 'global'): ")
    print(get_trending_stocks(prompt))










# import yfinance as yf
# from datetime import datetime

# # ✅ Optimized Indian stock list (Nifty50 + a few large caps)
# INDIAN_STOCKS = [
#     'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
#     'BAJFINANCE.NS', 'BAJAJFINSV.NS',
#     'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS',
#     'RELIANCE.NS', 'NTPC.NS',  'IOC.NS',
#     'TATAMOTORS.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS',
#     'SUNPHARMA.NS',
#     'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS',
#     'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS',
#     'ULTRACEMCO.NS', 'GRASIM.NS',
#     'BHARTIARTL.NS', 'DMART.NS'
# ]

# US_STOCKS = [
#     'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
#     'ADBE', 'INTC', 'AMD', 'CRM', 'PYPL', 'UBER', 'SHOP', 'SNOW',
#     'PLTR', 'BABA', 'JNJ', 'PFE', 'DIS'
# ]


# def get_trending_stocks(prompt: str = ""):
#     symbols = INDIAN_STOCKS + US_STOCKS
#     result = []

#     for sym in symbols:
#         try:
#             stock = yf.Ticker(sym)
#             info = stock.info
#             name = info.get("shortName", sym)
#             price = info.get("regularMarketPrice")
#             change = info.get("regularMarketChangePercent")

#             if price is not None and change is not None:
#                 result.append({
#                     "symbol": sym,
#                     "name": name,
#                     "price": price,
#                     "change": change
#                 })
#         except Exception:
#             continue

#     # Separate Indian and U.S. stocks
#     indian = [s for s in result if ".NS" in s["symbol"]]
#     us = [s for s in result if ".NS" not in s["symbol"]]

#     # Sorting
#     indian = sorted(indian, key=lambda x: x["change"], reverse=True)
#     us = sorted(us, key=lambda x: x["change"], reverse=True)

#     # Prompt Handling
#     prompt = prompt.lower()
#     top_n_india = 3
#     top_n_us = 2
#     show_india = show_us = False

#     if "top" in prompt:
#         if "india" in prompt:
#             show_india = True
#             try:
#                 top_n_india = int(prompt.split("top")[1].split()[0])
#             except:
#                 top_n_india = 5
#         elif "us" in prompt or "usa" in prompt or "america" in prompt:
#             show_us = True
#             try:
#                 top_n_us = int(prompt.split("top")[1].split()[0])
#             except:
#                 top_n_us = 5
#         elif "global" in prompt:
#             show_india = show_us = True
#             top_n_india, top_n_us = 3, 2
#         elif "stock" in prompt and "india" not in prompt and "us" not in prompt:
#             show_india = show_us = True
#             top_n_india = 1
#             top_n_us = 1
#     else:
#         show_india = show_us = True
        
        
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     output = "📊 Trending Stocks Today:\n\n"

#     if show_india:
#         output += f"🇮🇳 Top {top_n_india} Indian Stocks:\n"
#         for i, stock in enumerate(indian[:top_n_india], start=1):
#             emoji = "📈" if stock["change"] > 0 else "📉"
#             output += f"{i}. {emoji} {stock['name']} – ₹{stock['price']} ({round(stock['change'], 2)}%)\n"
#         output += "\n"

#     if show_us:
#         output += f"🇺🇸 Top {top_n_us} U.S. Stocks:\n"
#         for i, stock in enumerate(us[:top_n_us], start=1):
#             emoji = "📈" if stock["change"] > 0 else "📉"
#             output += f"{i}. {emoji} {stock['name']} – ${stock['price']} ({round(stock['change'], 2)}%)\n"

#     return output.strip()


# # Example usage
# if __name__ == "__main__":
#     prompt = input("Enter prompt (e.g., 'top 5 india', 'top 10 usa', 'global'): ")
#     print(get_trending_stocks(prompt))
