# Stock Screener

**IITISoC 2025 – Team FnQ-011**  
**Problem Statement #05**

---

## Team Details

- **Team Leader**: Nimai Gaba  
- **Team Members**: Lakshya Rishi, Lakshya Shukla, Aryama Singh  
- **Mentor**: Aryan

---

## Introduction

Modern financial markets generate massive volumes of OHLCV data every day. However, without contextual interpretation, this data becomes noise. While platforms like Bloomberg Terminal and TradingView cater to institutional users, they remain inaccessible to retail traders due to cost and complexity.

This project aims to bridge that gap by providing a lightweight, browser-based stock analysis and screening tool that enables users to access real-time data, forecasting, sentiment, and insights via an intuitive UI.

---

## Problem Statement and Objectives

**Objective:**  
Build a stock screening tool that filters equities using a combination of **fundamental**, **technical**, and **sentiment-based** indicators.

---

## Key Features

-  **Stock Screener** with live filtering (sector, volume, price change, etc.)
-  **TradingView-style Candlestick Charts** with technical indicators
-  **Portfolio Tracker** with real-time PnL updates (Firebase)
-  **Forecast Module** using Facebook Prophet
-  **Smart Chatbot** powered by Langchain + LLaMA
-  **Top Stories Feed** with sentiment from AlphaVantage

---

## System Modules

### 1.  Stock Screener
- Real-time screening via **yFinance API**
- Filters:
  - Sector
  - Market Cap
  - Volume
  - % Price Change
- `"BUY"` button simulates trades into portfolio

### 2. Interactive Charting
- Built using **Lightweight Charts** & **TradingView API**
- Technical Overlays:
  - SMA
  - EMA
  - RSI
  - MACD
  - ADX
- Features:
  - Crosshair tracking
  - Dynamic scaling
  - Timeframe zoom

### 3.  Forecast Engine
- Built using **Prophet (Meta)**
- Fetches historical OHLCV
- Forecast horizon: 7–30 days
- Visualized using **Plotly**
  - Tooltip hover
  - Forecast range bands

### 4. Portfolio Tracker
- Backed by **Firebase**
- Real-time price syncing
- PnL shown per stock & net
- User authentication and persistent session storage

### 5. Chatbot Assistant
- Langchain pipeline + **meta-LLaMA model**
- Responds to natural queries like:
  - “Trending Indian stocks”
  - “Give me Tesla sentiment”
- Fetches:
  - Live stats
  - Trends
  - Sentiment
- Returns clean, human-readable answers

### 6.  News Sentiment Feed
- Fetches headlines via **AlphaVantage API**
- Includes:
  - News source
  - Timestamp
  - Article URL
- No NLP used → Instant context delivery with minimal delay

## Tech Stack

| Tech                  | Usage                                 |
|-----------------------|----------------------------------------|
| React + Vite          | Frontend framework                     |
| Lightweight Charts    | Candlestick charting                   |
| Plotly                | Forecast visualizations                |
| Node.js               | Backend server for news feed           |
| Flask + FastAPI       | Backend API for yFinance + forecasting |
| Firebase (optional)   | Portfolio storage (only for contributors) |
| yFinance / TwelveData| Real-time stock data                   |
| Prophet               | Forecasting model                      |
| Langchain + LLaMA     | Smart Chatbot                          |
| Finnhub API           | News & sentiment analysis              |

---

## ⚙️ Setup Instructions

### Prerequisites

- Node.js (v18+ recommended)  
- Python 3.x  
- `yfinance`, `prophet`, `flask`, `fastapi`, `uvicorn` installed  

---

###  Run Locally

1. **Clone the Repository**

```bash
git clone https://github.com/NimaiGaba/Vridhi.git
cd stock-screener
```

2. **Install Frontend Dependencies**

```bash
npm install
```

3. **Start Backend Servers (in separate terminals)**

**Terminal A: Forecast & Stock Data (FastAPI)**

```bash
cd backend
uvicorn connect:app --reload
```

**Terminal B: News API (Node.js)**

```bash
cd server
node server.js
```

6. **Open the app in your browser**

```bash
http://localhost:5173
```
