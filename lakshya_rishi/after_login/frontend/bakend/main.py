from langchain.agents import Tool, initialize_agent
from .llm_config import llm
from .tools.get_trending import get_trending_stocks 
from .tools.get_sentiment import get_sentiment
from .tools.get_top_by_metric import get_top_by_metric_wrapper
from .tools.get_company_profile import get_company_profile
from .tools.get_comparison import get_comparison
from .tools.get_market_news_summary import get_market_news_summary
from .tools.get_low_risk_stocks import get_low_risk_stock
from .tools.get_recommendation import get_recommendation
from .tools.general import general_llm_response
import requests
from bs4 import BeautifulSoup
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')





tools = [
    Tool(
        name="get_company_profile",
        func=get_company_profile,
        description="Use this tool to get a short business description of a company. Example: 'Tell me about Infosys'."
    ),
    
    Tool(
    name="get_trending",
    func=lambda prompt: get_trending_stocks(prompt),
    description=(
        "Use this tool to get top trending stocks.\n"
        "- Example: 'Show trending stocks today'\n"
        "- Example: 'Give me top 5 Indian stocks'\n"
        "- Example: 'Top 10 USA stocks'\n"
        "- Example: 'Top 10 Indian stocks'\n"

        "- Example: 'Give global trending stocks'\n"
        "Returns top performing Indian (NSE) and/or US stocks based on percent gain."
    )
),

    
 Tool(
    name="get_top_by_metric",
    func=get_top_by_metric_wrapper,
    description=(
        "Use this tool to get top stocks by financial metric.\n"
        "Understands phrases like 'most profitable company', 'top eps stocks', 'lowest pe ratio'.\n"
        "Supported metrics: return, roe, eps, pe_ratio,\n"
        "Input example: 'metric=roe, top_n=3' or 'metric=return, period_days=30'"
    )
)
    ,
    
    Tool(
        name="get_market_news",
        func=get_market_news_summary,
        description="Use this to get the latest USA stock market headlines. Ex: 'Give me today’s market news'"
    ),
    
    Tool(
        name="get_comparison",
        func=get_comparison,
        description="Use this to compare two stocks across key metrics like PE, ROE, revenue, etc."
    ),
    
     Tool(
        name="get_low_risk_stock",
        func=get_low_risk_stock,
        description="Use this to get safe, low-volatility stocks with good ROE and EPS, low risk. Input: number of stocks to return (e.g., 5)"
        
    ),
#     Tool(
#     name="should_i_buy",
#     func=should_i_buy,
#     description="Takes in a U.S. company name and returns a Buy/Hold/Avoid recommendation. Only for US stocks. Example: 'should i buy tesla stock','should i buy apple stock'"
# )

#      ,
     Tool(
    name="get_recommendation",
    func=get_recommendation,
    description="Use this to get 2–3 stock recommendations for today. Example: 'Which stock should I buy today?','suggest me stock to buy','recommend stock to buy'"
)
     ,
     Tool(
        name="general_llm",
        func=general_llm_response,
        description="Use this tool for general or unrelated questions. Example: 'What is AI?', 'How does the stock market work?'",
        return_direct=True
    )
     
     ,
     Tool(
         name='get_sentiment',
         func=get_sentiment,
         description="Use this tool for getting sentiment of US stocks . Example:'Give me sentiment about apple,'sentiment about netflix''",
         return_direct=True
         )
#      ,
#      Tool(
#     name="get_company_news",
#     func=get_company_news,
#     description="Use this to get the latest news headlines for a specific US stock. If it returns a message starting with [STOP], do NOT use any more tools."
# )



]



agent = initialize_agent(
    tools,
    llm,
    agent_type="openai-tools",
    verbose=True,
    handle_parsing_errors=True
)

if __name__ == "__main__":
    while True:
        user_input = input("Ask your question: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        try:
            response = agent.invoke({"input": user_input})
            print("🤖", response)
        except Exception as e:
            print("⚠️ Error:", e)

# connecting the bot 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_config import llm

# ----- FASTAPI SETUP -----
app = FastAPI()

# Enable CORS so frontend can access this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request format from frontend
class ChatRequest(BaseModel):
    message: str

# API route to receive messages from frontend
@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.message.strip()
    user_input_clean = re.sub(r"[^\w\s]", "", user_input.lower())

    greetings = ["hi", "hello", "hey", "hii", "helo"]
    
    # ✅ Manually intercept greetings and directly return Smart Stock Assistant greeting
    if user_input_clean in greetings:
        response = general_llm_response(user_input)
        return {"response": response}
    
    # 👇 Otherwise let the agent decide
    try:
        print("User said:", user_input)
        response = agent.invoke({"input": user_input})
        print("Bot raw response:", response)
        return {"response": response["output"]}
    except Exception as e:
        print("❌ Error in /chat:", e)
        return {"response": "Sorry, the bot crashed!"}



# ----- (OPTIONAL) RETAIN TERMINAL CHAT TOO -----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
@app.get("/")
def root():
    return {"message": "FastAPI Chatbot API is running"}
