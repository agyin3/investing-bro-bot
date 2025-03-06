from alpaca.data.requests import StockLatestTradeRequest, StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from config.settings import API_KEY, API_SECRET
import pandas as pd
from alpaca.data.timeframe import TimeFrame  # ✅ Ensure TimeFrame is imported

# Initialize Alpaca Data Client (for historical and real-time data)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

def get_real_time_price(symbol):
    """Fetches the latest real-time price of a stock."""
    request_params = StockLatestTradeRequest(symbol_or_symbols=symbol)
    latest_trade = data_client.get_stock_latest_trade(request_params)
    
    return latest_trade[symbol].price if symbol in latest_trade else None


def get_historical_data(symbol, start_date, end_date, timeframe="day"):
    """Fetches historical stock data from Alpaca."""
    tf_map = {
        "1Min": TimeFrame.Minute,
        "5Min": TimeFrame(5, TimeFrame.Minute),
        "15Min": TimeFrame(15, TimeFrame.Minute),
        "day": TimeFrame.Day
    }
    
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=tf_map[timeframe],
        start=start_date,
        end=end_date
    )
    
    bars = data_client.get_stock_bars(request_params).df

    return bars
