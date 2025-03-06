from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config.settings import trading_client
from data.market_data import get_real_time_price
from trading.risk_management import set_stop_loss, set_take_profit
from notifications.telegram import send_telegram_message

# Track executed trades
open_trades = {}

def get_available_cash():
    """Fetches available cash in the Alpaca account."""
    account = trading_client.get_account()
    return float(account.cash)  # Convert to float for calculations

def execute_trade(symbol, qty, action, strategy="swing"):
    """Executes a trade, sets stop-loss & take-profit, and sends a Telegram notification."""
    
    order_side = OrderSide.BUY if action == "buy" else OrderSide.SELL
    time_in_force = TimeInForce.GTC if strategy == "swing" else TimeInForce.DAY

    # Get real-time price
    last_price = get_real_time_price(symbol)

    if last_price is None:
        print(f"⚠️ Could not retrieve price for {symbol}. Skipping trade.")
        return

    # Place order
    order_request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=time_in_force
    )

    trading_client.submit_order(order_request)

    # Set stop-loss and take-profit
    stop_loss_price = set_stop_loss(last_price)
    take_profit_price = set_take_profit(last_price)

    # Store trade details
    open_trades[symbol] = {
        "entry_price": last_price,
        "stop_loss": stop_loss_price,
        "take_profit": take_profit_price,
        "qty": qty,
        "action": action
    }

    # Send Telegram Alert
    message = f"📈 *Trade Executed*\n\n" \
              f"🔹 *Stock:* {symbol}\n" \
              f"🔹 *Action:* {action.capitalize()}\n" \
              f"🔹 *Entry Price:* ${last_price:.2f}\n" \
              f"🔹 *Stop-Loss:* ${stop_loss_price:.2f}\n" \
              f"🔹 *Take-Profit:* ${take_profit_price:.2f}\n"

    send_telegram_message(message)

    print(f"{action.capitalize()}ing {qty} shares of {symbol} at ${last_price:.2f}. Stop-Loss: ${stop_loss_price:.2f}, Take-Profit: ${take_profit_price:.2f}")
