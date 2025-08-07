# tools/general.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm_config import llm  # Import your configured LLM

def general_llm_response(question: str) -> str:
    """
    📌 General Purpose Tool Function

    - Responds with a friendly greeting if input is a greeting.
    - Else, uses LLM to get a short, emoji-enhanced reply.
    - Falls back to a default short response if LLM fails.

    Parameters:
        question (str): The user's input query.

    Returns:
        str: Custom message or LLM response with emojis and line breaks.
    """

    q_lower = question.strip().lower()
    greetings = ["hello", "hi", "hey", "hii", "helo"]

    if q_lower in greetings:
        return (
            "👋 Hello! I’m your Smart Stock Assistant.\n"
            "Here’s what I can help you with:\n"
            "1. 📈 Show trending or top-performing stocks\n"
            "2. 📊 Compare two companies\n"
            "3. 💡 Recommend good options of stock\n"
            "4. 📰 Summarize today’s market news\n"
            "5. 💬 Analyze stock sentiment (U.S. stocks only)\n"
            "6. 🔍 Get safe or low-risk stocks to invest in\n"
            "7. 🏆 Tell you the most profitable companies (like highest EPS, ROE, etc.)\n"
            "8. ❓ Answer general stock market questions\n\n"
            "Just ask me anything!"
        )

    try:
        # Ask LLM for short, emoji-friendly answer
        response = llm.invoke(
            f"Reply to this in 4 5  short line with emojis if suitable: {question}"
        )
        return response.content.strip()
    except Exception as e:
        return "🤖 Sorry, I couldn’t fetch a response. Please try again later!"
