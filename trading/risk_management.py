def set_stop_loss(entry_price, stop_loss_pct=2):
    """Calculates stop-loss price (default: 2% below entry price)."""
    return entry_price * (1 - stop_loss_pct / 100)

def set_take_profit(entry_price, take_profit_pct=5):
    """Calculates take-profit price (default: 5% above entry price)."""
    return entry_price * (1 + take_profit_pct / 100)
