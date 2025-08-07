import yfinance as yf
from tabulate import tabulate
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Add parent dir

from llm_config import llm  # uses mistral/groq or any configured LLM

# ✅ Standardized ticker mapping (lowercased)
TICKER_MAP = {
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL", "amazon": "AMZN", "meta": "META",
    "tesla": "TSLA", "nvidia": "NVDA", "adobe": "ADBE", "netflix": "NFLX", "salesforce": "CRM",
    "intel": "INTC", "amd": "AMD", "johnson & johnson": "JNJ", "pfizer": "PFE", "disney": "DIS",
    "alibaba": "BABA", "uber": "UBER", "paypal": "PYPL", "shopify": "SHOP", "palantir": "PLTR",

    "reliance": "RELIANCE.NS", "tcs": "TCS.NS", "infosys": "INFY.NS", "itc": "ITC.NS",
    "hdfc": "HDFCBANK.NS", "icici": "ICICIBANK.NS", "sbi": "SBIN.NS", "bajaj finance": "BAJFINANCE.NS",
    "hcl": "HCLTECH.NS", "l&t": "LT.NS", "coal india": "COALINDIA.NS", "sun pharma": "SUNPHARMA.NS",
    "divis": "DIVISLAB.NS", "maruti": "MARUTI.NS", "tata motors": "TATAMOTORS.NS", "irctc": "IRCTC.NS"
}

def resolve_company_name(user_input: str) -> str:
    """
    Returns the best-matched company name using LLM if not found directly in TICKER_MAP.
    """
    cleaned_input = user_input.strip().lower()
    if cleaned_input in TICKER_MAP:
        return cleaned_input  # exact match

    # Fuzzy match with LLM
    options = list(TICKER_MAP.keys())
    prompt = f"""
The user entered a company name: "{user_input}"

Choose the closest match from this list:
{options}

Just reply with the best-matched name.
"""
    try:
        match = llm.invoke(prompt).content.strip().lower()
        return match if match in TICKER_MAP else cleaned_input
    except Exception:
        return cleaned_input

def get_comparison(input_string: str) -> str:
    try:
        stock1, stock2 = [s.strip() for s in input_string.split(",")]
    except:
        return "❌ Please provide two company names separated by a comma. Example: 'TCS, Infosys'"

    # ✅ Now call the actual logic using extracted names
    return compare_companies(stock1, stock2)

def compare_companies(stock1: str, stock2: str) -> str:
    name1 = resolve_company_name(stock1)
    name2 = resolve_company_name(stock2)

    ticker1 = TICKER_MAP.get(name1, stock1.upper())
    ticker2 = TICKER_MAP.get(name2, stock2.upper())

    try:
        data1 = yf.Ticker(ticker1).info
        data2 = yf.Ticker(ticker2).info

        rows = [
            ["Company", name1.title(), name2.title()],
            ["Market Cap", f"{data1.get('marketCap', 'N/A'):,}", f"{data2.get('marketCap', 'N/A'):,}"],
            ["P/E Ratio", data1.get("trailingPE", "N/A"), data2.get("trailingPE", "N/A")],
            ["ROE", round(data1.get("returnOnEquity", 0) * 100, 2) if data1.get("returnOnEquity") else "N/A",
             round(data2.get("returnOnEquity", 0) * 100, 2) if data2.get("returnOnEquity") else "N/A"],
            ["Profit Margin", round(data1.get("profitMargins", 0) * 100, 2) if data1.get("profitMargins") else "N/A",
             round(data2.get("profitMargins", 0) * 100, 2) if data2.get("profitMargins") else "N/A"],
            ["Revenue (TTM)", f"{data1.get('totalRevenue', 'N/A'):,}", f"{data2.get('totalRevenue', 'N/A'):,}"],
            ["Dividend Yield", round(data1.get("dividendYield", 0) * 100, 2) if data1.get("dividendYield") else "0%",
             round(data2.get("dividendYield", 0) * 100, 2) if data2.get("dividendYield") else "0%"]
        ]

        table = tabulate(rows, headers="firstrow", tablefmt="github")
        return f"📊 **Comparison of {name1.title()} vs {name2.title()}:**\n\n```\n{table}\n```"

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ CLI usage
if __name__ == "__main__":
    company1 = input("Enter first company: ")
    company2 = input("Enter second company: ")
    print(get_comparison(f"{company1}, {company2}"))
