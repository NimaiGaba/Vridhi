from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
from prophet import Prophet
import pandas as pd

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class ForecastRequest(BaseModel):
    ticker: str
    period: int

# Utility function
def get_stock_data(ticker: str) -> pd.DataFrame:
    data = yf.download(ticker, period="5y", interval="1d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    data = data.dropna(subset=["Close"])
    data.reset_index(inplace=True)
    return data[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})

# Root route (optional)
@app.get("/")
def root():
    return {"message": "FastAPI Forecasting API is running"}

# Forecast route
@app.post("/forecast")
def forecast(req: ForecastRequest):
    df = get_stock_data(req.ticker)

    if df.empty:
        return {"error": "Invalid stock data"}

    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=req.period)
    forecast = model.predict(future)
    forecast_filtered = forecast.tail(req.period)[['ds', 'yhat']]

    return forecast_filtered.to_dict(orient="records")