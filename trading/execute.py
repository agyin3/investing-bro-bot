from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config.settings import trading_client
from data.market_data import get_real_time_price
from trading.risk_management import set_stop_loss, set_take_profit
from notifications.telegram import send_telegram_message

# ✅ Track open trades
open_trades = {}

def execute_trade(symbol, qty, action, strategy="swing"):
    """Executes a trade, calculates profit/loss, and sends a Telegram notification."""
    
    order_side = OrderSide.BUY if action == "buy" else OrderSide.SELL
    time_in_force = TimeInForce.GTC if strategy == "swing" else TimeInForce.DAY

    # ✅ Get real-time stock price
    last_price = get_real_time_price(symbol)

    if last_price is None:
        print(f"⚠️ Could not retrieve price for {symbol}. Skipping trade.")
        return

    # ✅ Submit trade order
    order_request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=time_in_force
    )

    trading_client.submit_order(order_request)

    # ✅ If it's a buy, store the trade details
    if action == "buy":
        open_trades[symbol] = {
            "entry_price": last_price,
            "qty": qty,
            "strategy": strategy
        }

    # ✅ If it's a sell, calculate profit/loss
    profit_loss = None
    if action == "sell" and symbol in open_trades:
        entry_price = open_trades[symbol]["entry_price"]
        profit_loss = round((last_price - entry_price) * qty, 2)
        del open_trades[symbol]  # ✅ Remove from open trades

    # ✅ Send Telegram notification
    message = f"📢 *Trade Executed!*\n\n" \
              f"🔹 *Stock:* {symbol}\n" \
              f"🔹 *Action:* {action.capitalize()}\n" \
              f"🔹 *Price:* ${last_price:.2f}\n" \
              f"🔹 *Quantity:* {qty}\n" \
              f"🔹 *Strategy:* {strategy.capitalize()}\n"

    if profit_loss is not None:
        message += f"💰 *Profit/Loss:* ${profit_loss:.2f}\n"

    send_telegram_message(message)

    print(f"{action.capitalize()}ing {qty} shares of {symbol} at ${last_price:.2f}.")
