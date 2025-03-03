import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from notifications.telegram_bot import send_telegram_alert

# Load environment variables
load_dotenv()
ALPACA_TEST_API_KEY = os.getenv("ALPACA_TEST_API_KEY")
ALPACA_TEST_SECRET_KEY = os.getenv("ALPACA_TEST_SECRET_KEY")

# Initialize Alpaca Trading Client
trading_client = TradingClient(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY)

def place_trade(symbol: str, action: str, qty: int):
    """
    Places a market order using Alpaca API.
    """
    try:
        side = OrderSide.BUY if action.lower() == "buy" else OrderSide.SELL

        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.GTC
        )

        trading_client.submit_order(order)
        message = f"📈 Trade Executed: {action.upper()} {qty} shares of {symbol}"
        send_telegram_alert(message)
        print(message)

    except Exception as e:
        error_message = f"⚠️ Trade Error: {e}"
        send_telegram_alert(error_message)
        print(error_message)