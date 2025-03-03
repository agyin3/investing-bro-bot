import time
from trading.trade_executor import place_trade
from trading.risk_management import risk_managed_trade
from backtesting.backtest import backtest_strategy
from utils.helpers import get_tradeable_stocks, get_portfolio_positions
from notifications.telegram_bot import send_telegram_alert

# Debug: Log script start
print("🚀 Starting Trading Bot...")
send_telegram_alert("🚀 Starting Trading Bot...")

# Fetch stocks in portfolio
portfolio = get_portfolio_positions()

# Check if any holdings have reached profit target
for symbol, data in portfolio.items():
    target_price = data["entry_price"] * 1.20  # 20% profit target

    if data["current_price"] >= target_price:
        print(f"💰 Selling {symbol}: Reached 20% profit target!")
        send_telegram_alert(f"💰 Selling {symbol}: Reached 20% profit target!")
        place_trade(symbol, "sell", data["qty"])


# Automatically fetch stocks under $5
SYMBOLS = get_tradeable_stocks()
print(f"📊 Selected Stocks for Analysis (Under $5): {SYMBOLS}")

if not SYMBOLS:
    print("❌ No tradable stocks found. Exiting.")
    send_telegram_alert("❌ No tradable stocks found. Exiting.")
    exit()

# Monitor & Trade Selected Stocks
for symbol in SYMBOLS:
    print(f"🔍 Analyzing {symbol}")

    # Run backtest before making a decision
    performance = backtest_strategy(symbol)

    # Debug: Print backtest result
    print(f"🔄 Backtest Result for {symbol}: {performance}")

    # If the backtest is successful, determine whether to place a normal trade or a risk-managed trade
    if performance and performance.get("success"):
        if performance.get("risk_score", 0) > 7:  # Assuming a risk score out of 10
            print(f"⚠️ High Risk: Executing Risk-Managed Trade for {symbol}")
            send_telegram_alert(f"⚠️ High Risk: Executing Risk-Managed Trade for {symbol}")
            risk_managed_trade(symbol, "buy", 10)
        else:
            print(f"✅ Low Risk: Executing Normal Trade for {symbol}")
            send_telegram_alert(f"✅ Low Risk: Executing Normal Trade for {symbol}")
            place_trade(symbol, "buy", 10)

    # Wait before checking the next stock
    time.sleep(5)

print("✅ Trading Bot Finished Execution")
send_telegram_alert("✅ Trading Bot Finished Execution")
