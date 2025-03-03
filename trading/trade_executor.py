import alpaca_trade_api as tradeapi
from config.config import ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY, ALPACA_TEST_BASE_URL
from notifications.telegram_bot import send_telegram_alert

api = tradeapi.REST(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY, ALPACA_TEST_BASE_URL, api_version='v2')

def place_trade(symbol, action, qty):
    """
    Executes a trade (buy/sell) using Alpaca API and sends a Telegram notification.
    """
    try:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=action,
            type="market",
            time_in_force="gtc"
        )
        message = f"📈 Trade Executed: {action.upper()} {qty} shares of {symbol}"
        send_telegram_alert(message)
        print(message)
    except Exception as e:
        error_message = f"⚠️ Trade Error: {e}"
        send_telegram_alert(error_message)
        print(error_message)

# Example: Buy 10 shares of AAPL
if __name__ == "__main__":
    place_trade("AAPL", "buy", 10)
