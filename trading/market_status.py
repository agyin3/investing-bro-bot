from alpaca.trading.client import TradingClient
from config.settings import API_KEY, API_SECRET
from datetime import datetime, timedelta
import pytz
import time
from notifications.telegram import send_telegram_message  # ✅ Import Telegram notifications

# Initialize Alpaca Trading Client
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

def is_market_open():
    """Checks if the stock market is currently open."""
    clock = trading_client.get_clock()
    return clock.is_open

def get_market_open_time():
    """Returns the market open time in UTC."""
    clock = trading_client.get_clock()
    return clock.next_open.astimezone(pytz.utc)  # ✅ Ensure timezone consistency

def get_market_close_time():
    """Returns the market close time in UTC."""
    clock = trading_client.get_clock()
    return clock.next_close.astimezone(pytz.utc)  # ✅ Ensure timezone consistency

def time_until_market_opens():
    """Returns the time in minutes until the market opens."""
    if is_market_open():
        return 0  # Market is already open

    now = datetime.utcnow().replace(tzinfo=pytz.utc)  # ✅ Ensure UTC timezone
    market_open_time = get_market_open_time()
    time_diff = (market_open_time - now).total_seconds() / 60  # ✅ Convert seconds to minutes

    return max(0, int(time_diff))

def wait_until_market_opens():
    """Pauses execution until 5 minutes before the market opens and sends a Telegram notification."""
    while not is_market_open():
        minutes_remaining = time_until_market_opens()
        
        if minutes_remaining > 5:
            print(f"📉 Market is closed. Sleeping for {minutes_remaining - 5} minutes until 5 minutes before open...")
            send_telegram_message(f"📉 *Market Closed.* The bot is paused until {minutes_remaining - 5} minutes before market open.")
            time.sleep((minutes_remaining - 5) * 60)  # Sleep until 5 minutes before open
        
        elif minutes_remaining > 0:
            print(f"⏳ Market opening soon. Waiting {minutes_remaining} more minutes...")
            send_telegram_message(f"⏳ *Market Opening Soon!* The bot is paused until market open.")
            time.sleep(60)  # Check every minute when it's close

    print("✅ Market is opening in 5 minutes. Resuming bot execution...")

    # ✅ Send Telegram notification
    send_telegram_message("🚀 *Market Opening Soon!* The bot is resuming trading in 5 minutes.")

def wait_until_market_closes():
    """Pauses execution until the market closes, then sends a Telegram notification."""
    while is_market_open():
        now = datetime.utcnow().replace(tzinfo=pytz.utc)  # ✅ Ensure timezone consistency
        market_close_time = get_market_close_time()
        time_until_close = (market_close_time - now).total_seconds() / 60  # ✅ Convert seconds to minutes
        
        if time_until_close > 5:
            print(f"📈 Market is open. Sleeping for {int(time_until_close - 5)} minutes until 5 minutes before close...")
            time.sleep((time_until_close - 5) * 60)  # Sleep until 5 minutes before close
        elif time_until_close > 0:
            print(f"⏳ Market closing soon. Waiting {int(time_until_close)} more minutes...")
            time.sleep(60)  # Check every minute when it's close

    print("📉 Market has closed. Pausing execution until next market open.")

    # ✅ Send Telegram notification
    send_telegram_message("📉 *Market Closed!* Trading has paused until the next market open.")
