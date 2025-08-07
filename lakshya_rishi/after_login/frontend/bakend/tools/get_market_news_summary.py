# get_market_news.py
import sys

import os
import requests
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Add parent dir

from llm_config import llm  # For summarization using Mistral/Groq LLM

def get_market_news_summary(_input: str = "") -> str:
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return "❌ FINNHUB_API_KEY not found in .env"

    # Fetch news from the past 3 days for general market
    today = datetime.now().date()
    three_days_ago = today - timedelta(days=3)

    url = "https://finnhub.io/api/v1/news"
    params = {
        "category": "general",  # general market news
        "from": three_days_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d"),
        "token": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            return "No recent general market news available."

        # Use only top 5 news articles
        selected_news = data[:5]
        news_text = ""
        for item in selected_news:
            date = datetime.fromtimestamp(item['datetime']).strftime('%Y-%m-%d')
            news_text += f"📅 {date} | 🏢 {item['source']}\n🔹 {item['headline']}\n\n"

        # Summarize with LLM
        # Summarize with LLM
        prompt = f"""You're a financial assistant. Read the following news headlines and summarize them in exactly 5 clear, concise bullet points.

        - Format: Each bullet point must start with a bold category like **[Topic]** followed by the summary.
        - Do not merge everything into a paragraph.
        - Keep it neat and readable.

        News headlines:
        {news_text}"""
        summary = llm.invoke(prompt).content


        return summary.strip()

    except Exception as e:
        return f"❌ Error fetching market news: {str(e)}"


# ✅ CLI usage
if __name__ == "__main__":
    print(get_market_news_summary())
