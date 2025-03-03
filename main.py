from trading.trade_executor import place_trade
from backtesting.backtest import backtest_strategy
from notifications.telegram_bot import send_telegram_alert
from utils.helpers import fetch_historical_data

# Notify Telegram bot startup
send_telegram_alert("🚀 Bot Started: Monitoring stock trades!")

# Fetch data & test strategy
symbol = "AAPL"
df = fetch_historical_data(symbol)
backtest_strategy(symbol)

# Execute trade
place_trade(symbol, "buy", 10)

# Notify completion
send_telegram_alert("✅ Trading Session Complete!")
