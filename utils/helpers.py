import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from trading.execute import place_trade
from trading.risk_management import risk_managed_trade
from backtesting.backtest import backtest_strategy
from notifications.telegram import send_telegram_alert

# Load environment variables
load_dotenv()
ALPACA_TEST_API_KEY = os.getenv("ALPACA_TEST_API_KEY")
ALPACA_TEST_SECRET_KEY = os.getenv("ALPACA_TEST_SECRET_KEY")

# Initialize Alpaca Clients
trading_client = TradingClient(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY)
data_client = StockHistoricalDataClient(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY)

# Set the daily investment limit
DAILY_INVESTMENT_LIMIT = 1000
remaining_investment = DAILY_INVESTMENT_LIMIT

def get_tradeable_stocks(min_price=0.01, max_price=100, min_volume=100000):
    """
    Fetches a list of tradeable stocks priced between $0.01 and $100 with at least the specified minimum volume and evaluates them using backtesting.
    """
    global remaining_investment
    print("🔍 Fetching and analyzing tradable stocks between $0.01 and $100...")
    assets = trading_client.get_all_assets(GetAssetsRequest(asset_class=AssetClass.US_EQUITY))
    
    for asset in assets:
        if remaining_investment <= 1:
            send_telegram_alert("🚨 Daily investment limit reached. Stopping further trades.")
            print("🚨 Daily investment limit reached. Stopping further trades.")
            return

        if asset.tradable and asset.status == "active" and asset.exchange in ["NYSE", "NASDAQ"]:
            try:
                # Fetch latest trade data to check price and volume
                trade_request = StockLatestTradeRequest(symbol_or_symbols=asset.symbol)
                latest_trade = data_client.get_stock_latest_trade(trade_request)
                price = latest_trade[asset.symbol].price
                volume = latest_trade[asset.symbol].size

                if not (min_price <= price <= max_price and volume >= min_volume):
                    continue

                # Fetch historical price data
                request_params = StockBarsRequest(symbol_or_symbols=asset.symbol, timeframe=TimeFrame.Day, limit=50)
                historical_data = data_client.get_stock_bars(request_params).df
                
                if historical_data.empty:
                    continue
                
                # Perform backtesting to determine best strategy
                performance = backtest_strategy(asset.symbol)
                
                if performance.get("success"):
                    send_telegram_alert(f"📈 Analyzing {asset.symbol} with best strategy: {performance['best_strategy']}")
                    execute_trade_based_on_backtesting(asset.symbol, performance["best_strategy"], performance.get("risk_score", 0))
            except Exception as e:
                print(f"⚠️ Skipping {asset.symbol}: {e}")
                continue  # Skip stocks without sufficient data

def execute_trade_based_on_backtesting(symbol, best_strategy, risk_score):
    """
    Executes trades based on backtesting results, choosing between normal or risk-managed trades.
    Takes into account the best strategy, risk score, and available investment budget.
    Automatically stops when the daily investment limit is reached.
    """
    global remaining_investment

    # Fetch latest stock price
    trade_request = StockLatestTradeRequest(symbol_or_symbols=symbol)
    latest_trade = data_client.get_stock_latest_trade(trade_request)
    price = latest_trade[symbol].price

    # Determine investment allocation dynamically
    max_trade_allocation = min(remaining_investment, DAILY_INVESTMENT_LIMIT * 0.5)  # Max 50% per trade
    qty = max(1, int(max_trade_allocation / price))  # Ensure at least 1 share is purchased

    if qty * price > remaining_investment:
        send_telegram_alert(f"⚠️ Not enough funds left to buy {symbol}. Skipping trade.")
        print(f"⚠️ Not enough funds left to buy {symbol}. Skipping trade.")
        return
    
    # Evaluate best strategy based on risk score and expected ROI
    risk_adjustment = 1.0 - (risk_score / 10)  # Scale down investment based on risk
    expected_roi_normal = price * (1.15 * risk_adjustment)  # Normal trade with adjusted 15% ROI target
    expected_roi_risk_managed = price * (1.2 * risk_adjustment)  # Risk-managed trade with adjusted 20% ROI target

    if expected_roi_risk_managed > expected_roi_normal and risk_score >= 5:
        print(f"⚠️ High Risk Trade: Executing Risk-Managed Trade for {symbol}, Buying {qty} shares at ${price}")
        send_telegram_alert(f"⚠️ High Risk Trade: Executing Risk-Managed Trade for {symbol}, Buying {qty} shares at ${price}")
        risk_managed_trade(symbol, "buy", qty)
    else:
        print(f"✅ Normal Trade: Executing Normal Trade for {symbol}, Buying {qty} shares at ${price}")
        send_telegram_alert(f"✅ Normal Trade: Executing Normal Trade for {symbol}, Buying {qty} shares at ${price}")
        place_trade(symbol, "buy", qty)
    
    # Deduct spent amount from remaining investment
    remaining_investment -= qty * price
    send_telegram_alert(f"💰 Remaining investment for the day: ${remaining_investment}")
    print(f"💰 Remaining investment for the day: ${remaining_investment}")
    
    if remaining_investment <= 1:
        send_telegram_alert("🚨 Daily investment limit reached. Stopping further trades.")
        print("🚨 Daily investment limit reached. Stopping further trades.")

def manage_portfolio(profit_target=1.15):
    """
    Checks current portfolio holdings and sells positions if profit target (15% ROI) is met.
    """
    print("🔍 Checking portfolio for profitable positions...")
    positions = trading_client.get_all_positions()
    
    for position in positions:
        symbol = position.symbol
        qty = int(position.qty)
        entry_price = float(position.avg_entry_price)
        current_price = float(position.current_price)
        target_price = entry_price * profit_target

        if current_price >= target_price:
            print(f"💰 Selling {symbol}: Reached {profit_target*100 - 100}% profit target!")
            send_telegram_alert(f"💰 Selling {symbol}: Reached {profit_target*100 - 100}% profit target!")
            place_trade(symbol, "sell", qty)
