import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, TakeProfitRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from notifications.telegram_bot import send_telegram_alert
from utils.helpers import get_live_price

# Load environment variables
load_dotenv()
ALPACA_TEST_API_KEY = os.getenv("ALPACA_TEST_API_KEY")
ALPACA_TEST_SECRET_KEY = os.getenv("ALPACA_TEST_SECRET_KEY")

# Initialize Alpaca Trading Client
trading_client = TradingClient(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY)

def risk_managed_trade(symbol: str, action: str, qty: int, stop_loss_pct: float = 5, take_profit_pct: float = 10):
    """
    Places a trade with stop-loss and take-profit settings using Alpaca API.
    """
    try:
        side = OrderSide.BUY if action.lower() == "buy" else OrderSide.SELL

        # Get current price
        entry_price = get_live_price(symbol)
        stop_loss_price = round(entry_price * (1 - stop_loss_pct / 100), 2)
        take_profit_price = round(entry_price * (1 + take_profit_pct / 100), 2)

        # Create order with stop-loss and take-profit
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.GTC,
            stop_loss=StopLossRequest(stop_price=stop_loss_price),
            take_profit=TakeProfitRequest(limit_price=take_profit_price)
        )

        trading_client.submit_order(order)
        message = (f"📊 Risk-Managed Trade: {action.upper()} {qty} shares of {symbol}\n"
                   f"🔻 Stop-Loss: ${stop_loss_price:.2f} | 🔺 Take-Profit: ${take_profit_price:.2f}")
        send_telegram_alert(message)
        print(message)
    
    except Exception as e:
        error_message = f"⚠️ Trade Error: {e}"
        send_telegram_alert(error_message)
        print(error_message)
