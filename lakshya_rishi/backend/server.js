const express = require('express');
const mongoose = require('mongoose');
const axios = require('axios');
const cron = require('node-cron');
const cors = require('cors');
require('dotenv').config();  // This should be your first line
const ALPHA_VANTAGE_KEY = process.env.ALPHA_VANTAGE_KEY || 'CL470XM2J4G9W15A';


const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/stock-news')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));
  
  // Update your news schema to match Alpha Vantage's structure
  const newsSchema = new mongoose.Schema({
    title: String,
    description: String,
    source: String,
    ticker: String,
    publishedAt: Date,
    url: String,
    imageUrl: String,
    category: String,
    sentiment: Number  // Optional: add if you want to track sentiment
  });
  const News = mongoose.model('News', newsSchema);

// Add your Alpha Vantage API key (get one from https://www.alphavantage.co/support/#api-key)
function parseAlphaDate(str) {
  // Alpha Vantage format: YYYYMMDDTHHMMSS
  if (!str || str.length !== 15) return null;
  const year = str.slice(0, 4);
  const month = str.slice(4, 6);
  const day = str.slice(6, 8);
  const hour = str.slice(9, 11);
  const minute = str.slice(11, 13);
  const second = str.slice(13, 15);
  return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}Z`);
}

// Replace the fetchStockNews function with this new version
async function fetchStockNews() {
  try {
    const response = await axios.get('https://www.alphavantage.co/query', {
      params: {
        function: 'NEWS_SENTIMENT',
        apikey: ALPHA_VANTAGE_KEY,
        limit: 100,
       
      }
    });

    console.log("Alpha Vantage Response:", response.data);

    if (!response.data.feed || !Array.isArray(response.data.feed)) {
      throw new Error('Alpha Vantage did not return news feed');
    }

    await News.deleteMany({});
    
    const articles = response.data.feed.map(article => ({
      title: article.title,
      description: article.summary,
      source: article.source,
      ticker: article.ticker_sentiment?.[0]?.ticker || 'GEN',
      publishedAt: parseAlphaDate(article.time_published), // ✅ fixed parsing
      url: article.url,
      imageUrl: article.banner_image || article.source_logo,
      category: 'financial'
    }));


    await News.insertMany(articles);
    console.log('News updated successfully from Alpha Vantage');
  } catch (error) {
    console.error('Error fetching Alpha Vantage news:', error.message);
    if (error.response) {
      console.error('Alpha Vantage error:', error.response.data);
    }
  }
}

// Schedule daily update at 8 AM
cron.schedule('0 8 * * *', fetchStockNews);

// Update the news endpoint to support pagination
app.get('/api/news', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    const news = await News.find()
      .sort({ publishedAt: -1 })
      .skip(skip)
      .limit(limit);
      
    res.json(news);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  fetchStockNews(); // Fetch news on startup
});