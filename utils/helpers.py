import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

# Load environment variables
load_dotenv()
ALPACA_TEST_API_KEY = os.getenv("ALPACA_TEST_API_KEY")
ALPACA_TEST_SECRET_KEY = os.getenv("ALPACA_TEST_SECRET_KEY")

# Initialize Alpaca Clients
trading_client = TradingClient(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY)
data_client = StockHistoricalDataClient(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY)

def get_tradeable_stocks(min_price=0.01, max_price=5, min_volume=100000):
    """
    Fetches a list of tradeable stocks priced below $5.
    """
    print("🔍 Fetching tradable stocks under $5...")
    assets = trading_client.get_all_assets(GetAssetsRequest(asset_class=AssetClass.US_EQUITY))
    tradable_stocks = []

    for asset in assets:
        if asset.tradable and asset.status == "active" and asset.exchange in ["NYSE", "NASDAQ"]:
            try:
                trade_request = StockLatestTradeRequest(symbol_or_symbols=asset.symbol)
                latest_trade = data_client.get_stock_latest_trade(trade_request)
                price = latest_trade[asset.symbol].price

                if min_price <= price <= max_price:
                    tradable_stocks.append(asset.symbol)
            except Exception as e:
                print(f"⚠️ Skipping {asset.symbol}: {e}")
                continue  # Skip stocks without sufficient data

    print(f"✅ Found {len(tradable_stocks)} tradable stocks under $5")
    return tradable_stocks

def get_live_price(symbol):
    """
    Fetches the latest price of a stock.
    """
    print(f"🔍 Fetching live price for {symbol}...")
    trade_request = StockLatestTradeRequest(symbol_or_symbols=symbol)
    latest_trade = data_client.get_stock_latest_trade(trade_request)
    price = float(latest_trade[symbol].price)
    print(f"💰 {symbol} Latest Price: ${price}")
    return price

def get_portfolio_positions():
    """
    Fetches current holdings in the Alpaca portfolio.
    Returns a dictionary with symbols, quantity, and entry prices.
    """
    positions = trading_client.get_all_positions()
    portfolio = {}

    for position in positions:
        portfolio[position.symbol] = {
            "qty": int(position.qty),
            "entry_price": float(position.avg_entry_price),
            "current_price": get_live_price(position.symbol)
        }

    return portfolio
