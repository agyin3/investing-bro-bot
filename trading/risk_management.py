import alpaca_trade_api as tradeapi
from config.config import ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY, ALPACA_TEST_BASE_URL
from notifications.telegram_bot import send_telegram_alert

def risk_managed_trade(symbol: str, action: str, qty: int, stop_loss_pct: float = 5, take_profit_pct: float = 10) -> None:
    """
    Places a trade with stop-loss and take-profit settings.
    """
    # Initialize Alpaca API
    api = tradeapi.REST(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY, ALPACA_TEST_BASE_URL, api_version='v2')
    
    try:
        # Get latest trade price
        quote = api.get_latest_trade(symbol)
        entry_price: float = round(float(quote.price), 2)  # Ensure two decimal places

        stop_loss_price: float = round(entry_price * (1 - stop_loss_pct / 100), 2)
        take_profit_price: float = round(entry_price * (1 + take_profit_pct / 100), 2)

        # Submit trade order with stop-loss and take-profit
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=action.lower(),
            type="market",
            time_in_force="gtc",
            order_class="bracket",
            stop_loss={"stop_price": stop_loss_price},
            take_profit={"limit_price": take_profit_price}
        )

        message = (f"📊 Risk-Managed Trade: {action.upper()} {qty} shares of {symbol}\n"
                   f"🔻 Stop-Loss: ${stop_loss_price:.2f} | 🔺 Take-Profit: ${take_profit_price:.2f}")
        send_telegram_alert(message)
        print(message)
    
    except Exception as e:
        error_message = f"⚠️ Trade Error: {e}"
        send_telegram_alert(error_message)
        print(error_message)

# Example: Buy 5 shares of TSLA with risk management
if __name__ == "__main__":
    risk_managed_trade("TSLA", "buy", 5)
