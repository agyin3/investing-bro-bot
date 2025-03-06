import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# Load environment variables
load_dotenv()

# Alpaca API Credentials
API_KEY = os.getenv("ALPACA_TEST_API_KEY")
API_SECRET = os.getenv("ALPACA_TEST_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_TEST_BASE_URL")  # Use live URL for real trading

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize Alpaca Trading Client
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)  # Set `paper=False` for live trading

# List of stocks to monitor
STOCKS = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN"]
