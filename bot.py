from strategies.swing_trade import swing_trade_strategy
from strategies.day_trade import day_trade_strategy
from trading.execute import execute_trade, open_trades
from trading.market_status import is_market_open, wait_until_market_opens, wait_until_market_closes
from backtesting.backtest import run_swing_trade_backtest, run_day_trade_backtest
from data.market_data import get_real_time_price
from notifications.telegram import send_telegram_message
from config.settings import STOCKS
import time

INTERVAL = 60  # ✅ Check every 60 seconds when market is open
QTY = 10  # ✅ Default quantity per trade

def exit_trade(symbol):
    """Exits a trade early if stop-loss or take-profit is triggered."""
    if symbol not in open_trades:
        return

    real_time_price = get_real_time_price(symbol)
    if real_time_price is None:
        return

    trade_details = open_trades[symbol]

    if real_time_price <= trade_details["stop_loss"]:
        print(f"🚨 {symbol} hit STOP-LOSS at ${real_time_price:.2f}. Exiting trade.")
        execute_trade(symbol, trade_details["qty"], "sell")
        del open_trades[symbol]

    elif real_time_price >= trade_details["take_profit"]:
        print(f"🎯 {symbol} hit TAKE-PROFIT at ${real_time_price:.2f}. Exiting trade.")
        execute_trade(symbol, trade_details["qty"], "sell")
        del open_trades[symbol]

def trading_bot():
    approved_stocks = {}
    market_was_closed = True  # ✅ Only rerun backtests when market was previously closed

    while True:
        if not is_market_open():
            wait_until_market_opens()  # ✅ Sleeps until 5 minutes before market opens
            market_was_closed = True  # ✅ Ensures backtests are refreshed

        if market_was_closed:
            print("📊 Running backtests at market open...")
            approved_stocks.clear()  # ✅ Clear old backtest results

            for symbol in STOCKS:
                swing_backtest = run_swing_trade_backtest(symbol)
                day_trade_backtest = run_day_trade_backtest(symbol)

                if swing_backtest and day_trade_backtest:
                    swing_pass = swing_backtest["win_rate"] >= 60 and swing_backtest["profit_loss_pct"] > 5
                    day_trade_pass = day_trade_backtest["win_rate"] >= 60 and day_trade_backtest["profit_loss_pct"] > 5

                    if swing_pass or day_trade_pass:
                        approved_stocks[symbol] = {"swing": swing_pass, "day_trade": day_trade_pass}
                        print(f"✅ Approved {symbol} for trading (Swing: {swing_pass}, Day Trade: {day_trade_pass})")
                    else:
                        print(f"❌ Skipping {symbol} (Swing: {swing_pass}, Day Trade: {day_trade_pass})")

            if not approved_stocks:
                print("⚠️ No stocks passed the backtest criteria. Pausing until next market open.")
                wait_until_market_closes()
                continue  # ✅ Skip to next loop iteration

            market_was_closed = False  # ✅ Reset flag since backtests have been rerun

        for symbol, strategies in approved_stocks.items():
            exit_trade(symbol)  # ✅ Check if stop-loss or take-profit is hit before making new trades

            if strategies["swing"]:
                print(f"Checking {symbol} for swing trades...")
                swing_df = swing_trade_strategy(symbol)
                latest_swing_signal = swing_df["Signal"].iloc[-1]
                if latest_swing_signal == 1:
                    execute_trade(symbol, QTY, "buy", strategy="swing")

            if strategies["day_trade"]:
                print(f"Checking {symbol} for day trades...")
                day_df = day_trade_strategy(symbol)
                latest_day_signal = day_df["Signal"].iloc[-1]
                if latest_day_signal == 1:
                    execute_trade(symbol, QTY, "buy", strategy="day")

        time.sleep(INTERVAL)  # ✅ Runs every 60 seconds when market is open

if __name__ == "__main__":
    trading_bot()
