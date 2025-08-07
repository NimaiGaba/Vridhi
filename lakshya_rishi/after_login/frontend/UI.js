import {
  auth,
  db,
  firebaseDoc,
  firebaseSignOut,
  firebaseSetDoc,
  firebaseGetDoc,
  firebaseOnAuthStateChanged
} from '../../../login_page/firebase-config.js';

let currentNewsPage = 1;
// Mapping dropdown indicators to TradingView codes
const indicatorMap = {
  "SMA": "MASimple@tv-basicstudies",
  "EMA": "MAExp@tv-basicstudies",
  "MACD": "MACD@tv-basicstudies",
  "ADX": "ADX@tv-basicstudies",
  "RSI": "RSI@tv-basicstudies",
  "Stochastic Oscillator": "StochasticRSI@tv-basicstudies",
  "CCI": "CCI@tv-basicstudies",
  "Bollinger Bands": "BollingerBands@tv-basicstudies",
  "ATR": "ATR@tv-basicstudies",
  "OBV": "OBV@tv-basicstudies",
  "Chaikin Money Flow": "CMF@tv-basicstudies"
};

let selectedIndicators = []; // Will store applied indicators

const newsPerPage = 10; // Number of news items to load per request
let portfolioData = []; // Store user trades


function toggleChat() {
  const chat = document.getElementById('chatWindow');
  chat.style.display = chat.style.display === 'flex' ? 'none' : 'flex';
}

async function sendMessage() {
  const input = document.getElementById('userInput');
  const chatBody = document.getElementById('chatBody');
  const typingIndicator = document.getElementById('typingIndicator');

  const message = input.value.trim();
  if (message === '') return;

  // Show user's message
  const userMsg = document.createElement('div');
  userMsg.classList.add('chat-message', 'user');
  userMsg.textContent = message;
  chatBody.appendChild(userMsg);
  input.value = '';
  chatBody.scrollTop = chatBody.scrollHeight;

  // Show typing
  typingIndicator.style.display = 'block';

  try {
    const response = await fetch("http://127.0.0.1:8002/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message })
    });

    const data = await response.json();
    console.log("Bot response:", data);

    const botMsg = document.createElement('div');
    botMsg.classList.add('chat-message', 'bot');

    let formatted = data.response
      .replace(/\n/g, "\n")
      .replace(/\*\*(.*?)\*\*/g, "$1"); // Optional markdown bold cleanup

    botMsg.textContent = formatted;
    chatBody.appendChild(botMsg);
    chatBody.scrollTop = chatBody.scrollHeight;
  } catch (err) {
    console.error("Fetch error:", err);
    const errorMsg = document.createElement('div');
    errorMsg.classList.add('chat-message', 'bot');
    errorMsg.textContent = "Something went wrong.";
    chatBody.appendChild(errorMsg);
  } finally {
    typingIndicator.style.display = 'none';
  }
}
document.getElementById('userInput').addEventListener('keydown', function (event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // Prevents default behavior like adding a new line
    sendMessage();
  }
});

async function loadPortfolio() {
  const table = document.getElementById('portfolioTable');
  const totalBalanceElem = document.getElementById('totalBalance');
  const totalPnLElem = document.getElementById('totalPnL');

  let totalBalance = 0;
  let totalPnL = 0;

  table.innerHTML = "";

  for (let i = 0; i < portfolioData.length; i++) {
    const item = portfolioData[i];

    try {
      // Fetch live price for the stock
      const res = await fetch(`https://api.twelvedata.com/price?symbol=${item.symbol}&apikey=1901c3f6f2a547989034900aa84a2aa6`);
      const priceData = await res.json();

      const livePrice = parseFloat(priceData.price);
      const profitLoss = (livePrice - item.priceAtTransaction) * item.quantity;

      totalBalance += livePrice * item.quantity;
      totalPnL += profitLoss;

      const row = document.createElement('tr');
      row.className = 'hover:bg-gray-700 transition';

      row.innerHTML = `
              <td class="p-3">${i + 1}</td>
              <td class="p-3 text-blue-400">${item.symbol}</td>
              <td class="p-3">${item.name}</td>
              <td class="p-3">${item.orderType}</td>
              <td class="p-3">${item.orderMode}</td>
              <td class="p-3">${item.quantity}</td>
              <td class="p-3">$${item.priceAtTransaction.toFixed(2)}</td>
              <td class="p-3 text-green-400">$${livePrice.toFixed(2)}</td>
              <td class="p-3 text-${profitLoss >= 0 ? 'green' : 'red'}-400">$${profitLoss.toFixed(2)}</td>
              <td class="p-3">${item.datetime}</td>
            `;

      table.appendChild(row);
    } catch (err) {
      console.error(`Error fetching live price for ${item.symbol}:`, err);
    }
  }

  totalBalanceElem.textContent = `$${totalBalance.toFixed(2)}`;
  totalPnLElem.textContent = `$${totalPnL.toFixed(2)}`;
  totalPnLElem.className = totalPnL >= 0 ? 'text-green-400' : 'text-red-400';
}

function recordTrade() {
  const symbol = document.getElementById('symbolInput').value.trim().toUpperCase();
  const quantity = parseFloat(document.getElementById('qtyInput').value);
  const price = parseFloat(document.getElementById('priceInput').value);
  const orderType = document.getElementById('orderTypeInput').value;
  const now = new Date().toLocaleString();

  if (!symbol || !quantity || !price) return alert('Please fill all fields');

  // Simulate live price via small fluctuation
  const livePrice = price * (Math.random() * 0.1 + 0.95);

  portfolioData.push({
    symbol,
    name: symbol, // optional name
    quantity,
    priceAtTransaction: price,
    livePrice,
    orderType,
    orderMode: "Market",
    datetime: now
  });

  loadPortfolio(); // Refresh table
}

// Update the loadTopStories function
async function loadTopStories(page = 1, limit = 10) {
  try {
    const response = await fetch(`http://localhost:5000/api/news?page=${page}&limit=${limit}`);
    const stories = await response.json();

    const storiesContainer = document.getElementById('storiesContent');

    if (page === 1) {
      storiesContainer.innerHTML = '';
    }

    stories.forEach(story => {
      const timeAgo = formatTimeAgo(new Date(story.publishedAt));
      const ticker = story.ticker || 'GEN';

      const storyEl = document.createElement('div');
      storyEl.className = 'story-card p-4 mb-4 rounded-lg bg-gray-800 hover:bg-gray-700 transition cursor-pointer';
      storyEl.innerHTML = `
        <div class="flex flex-col sm:flex-row gap-4">
          <img src="${story.imageUrl || 'https://via.placeholder.com/150'}"
              alt="news image"
              class="w-full sm:w-48 h-32 object-cover rounded-lg mb-2 sm:mb-0">
          <div class="flex flex-col justify-between">
            <div>
              <div class="flex justify-between items-start mb-2">
                <span class="text-xs text-gray-400">${timeAgo}</span>
                <span class="text-xs font-semibold bg-blue-500 px-2 py-1 rounded">${ticker}</span>
              </div>
              <h3 class="text-lg font-semibold mb-2">${story.title}</h3>
              <p class="text-sm text-gray-300 mb-2">${story.description || ''}</p>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-xs text-gray-400">${story.source}</span>
              <a href="${story.url}" target="_blank" class="text-xs text-blue-400 hover:underline">Read more</a>
            </div>
          </div>
        </div>
      `;
      storiesContainer.appendChild(storyEl);
    });

    // Hide load more button if we've reached the end
    if (stories.length < limit) {
      document.getElementById('loadMoreStoriesBtn').style.display = 'none';
    }
  } catch (error) {
    console.error('Error loading stories:', error);
  }
}
async function loadPortfolioFromFirestore() {
  if (!auth.currentUser) return;

  try {
    const userRef = firebaseDoc(db, "users", auth.currentUser.uid);
    const docSnap = await firebaseGetDoc(userRef);

    if (docSnap.exists()) {
      portfolioData = docSnap.data().portfolio || [];
      loadPortfolio();  // Refresh UI
    }
  } catch (error) {
    console.error("Error loading portfolio:", error);
  }
}
async function savePortfolioToFirestore() {
  if (!auth.currentUser) return;

  try {
    const userRef = firebaseDoc(db, "users", auth.currentUser.uid);
    await firebaseSetDoc(userRef, { portfolio: portfolioData });
    console.log("Portfolio saved.");
  } catch (error) {
    console.error("Error saving portfolio:", error);
  }
}

function formatTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);

  let interval = Math.floor(seconds / 31536000);
  if (interval >= 1) return `${interval} year${interval === 1 ? '' : 's'} ago`;

  interval = Math.floor(seconds / 2592000);
  if (interval >= 1) return `${interval} month${interval === 1 ? '' : 's'} ago`;

  interval = Math.floor(seconds / 86400);
  if (interval >= 1) return `${interval} day${interval === 1 ? '' : 's'} ago`;

  interval = Math.floor(seconds / 3600);
  if (interval >= 1) return `${interval} hour${interval === 1 ? '' : 's'} ago`;

  interval = Math.floor(seconds / 60);
  if (interval >= 1) return `${interval} minute${interval === 1 ? '' : 's'} ago`;

  return `${Math.floor(seconds)} second${seconds === 1 ? '' : 's'} ago`;
}

function extractTicker(title) {
  const tickerPattern = /[A-Z]{2,5}/g;
  const matches = title.match(tickerPattern);
  return matches ? matches[0] : null;
}

// Update showSection function
function showSection(sectionId) {
  document.getElementById("default-widget").style.display = "none";
  document.querySelectorAll('#charting, #portfolio, #screener, #technical, #stories, #searchResultSection')
    .forEach(section => section.classList.add('hidden'));
  document.getElementById(sectionId).classList.remove('hidden');

  if (sectionId === 'portfolio') loadPortfolio();
  //   function selectCompany(symbol, name) {
  //   selectedSymbol = symbol;
  //   selectedTicker = symbol;  // <-- ensures forecast uses this company
  //   document.getElementById('selectCompanyBtn').innerText = `${name} (${symbol})`;
  //   document.getElementById('selectedCompany').textContent = symbol; // Update forecast section label
  //   loadTradingViewChart(symbol);
  //   closeCompanySelector();
  //   fetchForecast(); // <-- auto-refresh forecast when company changes
  // }


  if (sectionId === 'stories') loadTopStories();
}

document.getElementById('loadMoreStoriesBtn').addEventListener('click', () => {
  currentNewsPage++;
  loadTopStories(currentNewsPage);
});
// FIXED Place Order Function
async function placeOrderFromChart(context = "charting") {
  const symbolInputId = context === "search" ? "chartSymbol" : "chartingTickerInput";
  const quantityInputId = context === "search" ? "chartQuantity" : "chartQuantity"; // ❌ THIS IS WRONG
  // The issue is here: you're using the same ID, but both sections have elements with the same ID.

  const quantity = parseFloat(
    context === "search"
      ? document.querySelector('#searchResultSection #chartQuantity').value
      : document.querySelector('#charting #chartQuantity').value
  );

  const symbol = document.getElementById(symbolInputId).value.trim().toUpperCase();
  const orderType = document.getElementById('chartType').value;
  const now = new Date().toLocaleString();

  if (!symbol || !quantity) return alert('Please enter symbol and quantity');

  try {
    const res = await fetch(`https://api.twelvedata.com/price?symbol=${symbol}&apikey=1901c3f6f2a547989034900aa84a2aa6`);
    const data = await res.json();

    if (!data.price) {
      alert('Could not fetch live price. Check symbol.');
      return;
    }

    const price = parseFloat(data.price);

    portfolioData.push({
      symbol,
      name: symbol,
      quantity,
      priceAtTransaction: price,
      livePrice: price,
      orderType,
      orderMode: "Market",
      datetime: now
    });

    alert(`${orderType} Order placed for ${symbol} at $${price.toFixed(2)}`);
    loadPortfolio();
    await savePortfolioToFirestore();
  } catch (err) {
    console.error("Error placing order:", err);
    alert('Error placing order');
  }
}

// Profile Dropdown Toggle
document.getElementById('profileDropdownBtn').addEventListener('click', () => {
  const menu = document.getElementById('profileDropdownMenu');
  const backdrop = document.getElementById('profileBackdrop');
  menu.classList.toggle('hidden');
  menu.classList.toggle('show');
  backdrop.classList.toggle('hidden');  // Show/hide backdrop
});

// Close dropdown when clicking outside OR on backdrop
document.addEventListener('click', (event) => {
  const btn = document.getElementById('profileDropdownBtn');
  const menu = document.getElementById('profileDropdownMenu');
  const backdrop = document.getElementById('profileBackdrop');
  if ((!btn.contains(event.target) && !menu.contains(event.target)) || event.target === backdrop) {
    menu.classList.add('hidden');
    menu.classList.remove('show');
    backdrop.classList.add('hidden');
  }
});
// Open & close modal
let companySelectionContext = "";

function openCompanySelector(context = "") {
  companySelectionContext = context;
  document.getElementById('companyModal').classList.remove('hidden');
}

// Full company list
const companies = [
  { name: "Apple", symbol: "AAPL" },
  { name: "Amazon", symbol: "AMZN" },
  { name: "Alphabet (Google)", symbol: "GOOGL" },
  { name: "Microsoft", symbol: "MSFT" },
  { name: "Tesla", symbol: "TSLA" },
  { name: "Meta Platforms", symbol: "META" },
  { name: "NVIDIA", symbol: "NVDA" },
  { name: "Adobe", symbol: "ADBE" },
  { name: "Netflix", symbol: "NFLX" },
  { name: "Salesforce", symbol: "CRM" },
  { name: "Intel", symbol: "INTC" },
  { name: "AMD", symbol: "AMD" },
  { name: "Johnson & Johnson", symbol: "JNJ" },
  { name: "Pfizer", symbol: "PFE" },
  { name: "Disney", symbol: "DIS" },
  { name: "Alibaba", symbol: "BABA" },
  { name: "Uber", symbol: "UBER" },
  { name: "PayPal", symbol: "PYPL" },
  { name: "Shopify", symbol: "SHOP" },
  { name: "Palantir", symbol: "PLTR" },
  { name: "Reliance Industries", symbol: "RELIANCE.NS" },
  { name: "TCS", symbol: "TCS.NS" },
  { name: "Infosys", symbol: "INFY.NS" },
  { name: "ITC", symbol: "ITC.NS" },
  { name: "HDFC Bank", symbol: "HDFCBANK.NS" },
  { name: "ICICI Bank", symbol: "ICICIBANK.NS" },
  { name: "State Bank of India", symbol: "SBIN.NS" },
  { name: "Bajaj Finance", symbol: "BAJFINANCE.NS" },
  { name: "HCL Technologies", symbol: "HCLTECH.NS" },
  { name: "Larsen & Toubro", symbol: "LT.NS" },
  { name: "Coal India", symbol: "COALINDIA.NS" },
  { name: "Sun Pharma", symbol: "SUNPHARMA.NS" },
  { name: "Divi's Labs", symbol: "DIVISLAB.NS" },
  { name: "Maruti Suzuki", symbol: "MARUTI.NS" },
  { name: "Tata Motors", symbol: "TATAMOTORS.NS" },
  { name: "IRCTC", symbol: "IRCTC.NS" }
];

const companyListDiv = document.getElementById('companyList');
const searchInput = document.getElementById('companySearchInput');

function renderCompanyList(filter = '') {
  companyListDiv.innerHTML = '';
  companies
    .filter(c => c.name.toLowerCase().includes(filter.toLowerCase()) || c.symbol.toLowerCase().includes(filter.toLowerCase()))
    .forEach(c => {
      const div = document.createElement('div');
      div.className = "company-option";
      div.textContent = `${c.name} (${c.symbol})`;
      div.onclick = () => {
        if (companySelectionContext === "charting") {
          selectCompanyForCharting(c.symbol, c.name);
        } else if (companySelectionContext === "technical") {
          selectCompanyForTechnical(c.symbol, c.name);
        }
        closeCompanySelector(); // ✅ Ensures modal always closes
      };
      companyListDiv.appendChild(div);
    });
}
searchInput.addEventListener('input', (e) => renderCompanyList(e.target.value));

let selectedSymbol = "AAPL";

// For Charting section
function selectCompanyForCharting(symbol, name) {
  selectedSymbol = symbol;

  // Update Charting section UI
  const chartingBtn = document.getElementById('selectCompanyBtnCharting');
  if (chartingBtn) chartingBtn.innerText = `${name} (${symbol})`;

  const chartingLabel = document.getElementById('selectedCompanyCharting');
  if (chartingLabel) chartingLabel.textContent = symbol;

  // ✅ Set Ticker input in Charting Trade Panel
  const chartingTickerInput = document.getElementById('chartingTickerInput');
  if (chartingTickerInput) chartingTickerInput.value = symbol;

  // Load TradingView chart
  loadTradingViewChart(symbol);

  // Only close modal — no switching sections
  closeCompanySelector();
}

// For Technical Forecasting section
function selectCompanyForTechnical(symbol, name) {
  selectedTicker = symbol;

  const forecastBtn = document.getElementById('selectCompanyBtn');
  if (forecastBtn) forecastBtn.innerText = `${name} (${symbol})`;
  const forecastLabel = document.getElementById('selectedCompany');
  if (forecastLabel) forecastLabel.textContent = symbol;

  closeCompanySelector();
  fetchForecast();
}


// Directly load chart
function loadTradingViewChart(symbol) {
  document.getElementById('tradingview_advanced_chart').innerHTML = "";
  new TradingView.widget({
    "container_id": "tradingview_advanced_chart",
    "width": "100%",
    "height": 600,
    "symbol": symbol,
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#1f2937",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "withdateranges": true,
    "hide_side_toolbar": false,
    "studies": [],
    "support_host": "https://www.tradingview.com",
    "details": true,
    "hotlist": true,
    "calendar": true
  });
}
function closeCompanySelector() {
  const modal = document.getElementById('companyModal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

// Initial render
renderCompanyList();

function applyIndicator() {
  const selected = document.getElementById('indicatorSelect').value;
  if (!selected || selected === "Select Indicator") return;

  const study = indicatorMap[selected];
  if (study && !selectedIndicators.includes(study)) {
    selectedIndicators.push(study);  // Add new study
    loadTradingViewChart(selectedSymbol);  // Reload chart with all studies
  }
}

// Toggle the Period dropdown
document.getElementById('periodDropdownBtn').addEventListener('click', () => {
  const menu = document.getElementById('periodDropdownMenu');
  menu.classList.toggle('hidden');
});

// Close Period dropdown on outside click
document.addEventListener('click', (event) => {
  const btn = document.getElementById('periodDropdownBtn');
  const menu = document.getElementById('periodDropdownMenu');
  if (!btn.contains(event.target) && !menu.contains(event.target)) {
    menu.classList.add('hidden');
  }
});

// Store selected forecast period and company
let selectedTicker = "AAPL";     // Default company
let forecastPeriod = 30;         // Default forecast period (in days)

// Set forecast period from dropdown
function setForecastPeriod(days) {
  forecastPeriod = parseInt(days);
  document.getElementById("periodDropdownBtn").textContent = `${days} Days`;
  document.getElementById("periodDropdownMenu").classList.add("hidden");
}

// Open company selection modal

// Called when "Apply" button is clicked
async function fetchForecast() {
  if (!selectedTicker || !forecastPeriod) {
    alert("Please select a company and forecast period.");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8001/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticker: selectedTicker,
        period: forecastPeriod
      })
    });

    if (!response.ok) {
      alert("Failed to fetch forecast.");
      return;
    }

    const data = await response.json();
    drawForecastChart(data);
  } catch (error) {
    console.error("Error fetching forecast:", error);
    alert("Something went wrong while fetching forecast.");
  }
}


// Draw Plotly Forecast Chart
function drawForecastChart(forecastData) {
  const labels = forecastData.map(item => item.ds);
  const values = forecastData.map(item => item.yhat);

  const trace = {
    x: labels,
    y: values,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Forecasted Price',
    line: {
      color: 'skyblue'
    },
    marker: {
      color: 'lightblue'
    }
  };

  const layout = {
    title: {
      text: `${selectedTicker} - ${forecastPeriod} Day Forecast`,
      font: {
        color: 'white'
      }
    },
    plot_bgcolor: '#0c0d0eff',
    paper_bgcolor: '#0b0c0cff',
    font: {
      color: 'white'
    },
    xaxis: {
      title: 'Date'
    },
    yaxis: {
      title: 'Forecasted Price'
    }
  };

  Plotly.newPlot('forecastChart', [trace], layout, { responsive: true });
}

// Automatically fetch forecast on page load with default values
window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("selectedCompany").textContent = selectedTicker;
  document.getElementById("periodDropdownBtn").textContent = `${forecastPeriod} Days`;
  fetchForecast();
});
// Attach submit event
// Charting trade panel
// Charting trade panel
document.getElementById('chartTradeForm').addEventListener('submit', (e) => {
  e.preventDefault();
  placeOrderFromChart("charting");
});

// Search result trade panel
document.getElementById('searchResultTradeForm').addEventListener('submit', (e) => {
  e.preventDefault();
  placeOrderFromChart("search");
});

// Sidebar Search Functionality
// Sidebar Search Functionality (New)
document.getElementById('sidebarSearchBtn').addEventListener('click', () => {
  const query = document.getElementById('sidebarSearchInput').value.trim().toUpperCase();
  if (!query) return alert("Enter a stock name or symbol (e.g., Apple or AAPL)");

  // Try to find a match in companies list
  const companyMatch = companies.find(c =>
    c.name.toLowerCase().includes(query.toLowerCase()) || c.symbol.toLowerCase() === query.toLowerCase()
  );
  const finalSymbol = companyMatch ? companyMatch.symbol : query;

  // Open search result section
  showSection('searchResultSection');
  loadSearchResultChart(finalSymbol);
  document.getElementById('chartSymbol').value = finalSymbol; // ✅ Add this
});
document.getElementById('sidebarSearchInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    document.getElementById('sidebarSearchBtn').click();
  }
});
function loadSearchResultChart(symbol) {
  document.getElementById('searchResultChart').innerHTML = "";
  new TradingView.widget({
    "container_id": "searchResultChart",
    "width": "100%",
    "height": 600,
    "symbol": symbol,
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#1f2937",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "withdateranges": true,
    "hide_side_toolbar": false,
    "studies": [],
    "support_host": "https://www.tradingview.com",
    "details": true
  });
}
firebaseOnAuthStateChanged(auth, (user) => {
  const usernameEl = document.getElementById('profileUsername');
  const photoEl = document.getElementById('profilePhoto');

  if (user) {
    console.log("🔥 Firebase User Object:", user);

    const username = user.displayName || "User";
    usernameEl.textContent = username;

    if (user.photoURL) {
      photoEl.src = user.photoURL;
      console.log("✅ Using Google photo:", user.photoURL);
    } else {
      photoEl.src = "download (1).png";
      console.warn("❌ user.photoURL is missing");
    }

    loadPortfolioFromFirestore();
  } else {
    usernameEl.textContent = "Guest";
    photoEl.src = "download (1).png";
    console.log("⚠️ No user signed in.");
  }
});
gapi.load('auth2', () => {
  gapi.auth2.init();
});

async function logoutUser() {
  try {
    await firebaseSignOut(auth);

    // ✅ Clear auto-select session from Google Identity Services (if used)
    if (window.google?.accounts?.id) {
      google.accounts.id.disableAutoSelect();
    }

    // ✅ Redirect to login
    window.location.href = '/login_page/page.html';
  } catch (error) {
    console.error("Logout error:", error);
    alert("Error during logout. Please try again.");
  }
}

window.logoutUser = logoutUser;
window.showSection = showSection;
window.openCompanySelector = openCompanySelector;
window.closeCompanySelector = closeCompanySelector;
window.setForecastPeriod = setForecastPeriod;
window.fetchForecast = fetchForecast;
window.sendMessage = sendMessage;
window.toggleChat = toggleChat;
window.loadPortfolio = loadPortfolio;
window.recordTrade = recordTrade;