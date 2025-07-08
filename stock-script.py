import alpaca_trade_api as tradeapi
import pandas as pd
import time
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os
import threading
import requests
import csv

user_command = {"cmd": None}

def keyboard_listener():
    while True:
        key = input().strip().lower()
        if key in ['s', 'r']:
            user_command["cmd"] = key

load_dotenv()  # take environment variables from .env

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = os.getenv("ALPACA_BASE_URL")

STARTING_CASH = float(os.getenv("STARTING_CASH") or 100)
POSITIONS = 5
MAX_DAY_TRADES = 3
TRADING_DAYS = ['Monday', 'Tuesday', 'Wednesday']  # pick your preferred days

BULL_STOP_LOSS = -0.02    # -2% for bull
BULL_TAKE_PROFIT = 0.06   # +6% for bull
BEAR_STOP_LOSS = -0.01    # -1% for bear
BEAR_TAKE_PROFIT = 0.03   # +3% for bear

MAX_LOSING_TRADES = 2

DEFENSIVE_SECTORS = {
    "XLV": ["JNJ", "PFE", "MRK"],     # Healthcare
    "XLP": ["PG", "KO", "WMT"],       # Consumer Staples
    "XLU": ["NEE", "DUK", "SO"],      # Utilities
}
DEFAULT_CANDIDATES = [
    'AAPL', 'NVDA', 'TSLA', 'MSFT', 'META', 'AMZN',
    'AMD', 'NFLX', 'GOOG', 'SMCI', 'JNJ', 'PFE', 'MRK', 'PG', 'KO', 'WMT', 'NEE', 'DUK', 'SO'
]

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')
eastern = pytz.timezone('US/Eastern')
trade_log = {}

def get_account_equity():
    return float(api.get_account().equity)

def is_market_open():
    return api.get_clock().is_open

def get_market_status():
    """Return 'bull', 'bear', or 'choppy'."""
    spy_bars = api.get_bars('SPY', '5Min', limit=2).df
    if len(spy_bars) < 2:
        return "choppy"
    open_price = spy_bars['open'].iloc[0]
    last_price = spy_bars['close'].iloc[-1]
    change = (last_price - open_price) / open_price
    if change > 0.005:
        return 'bull'
    elif change < -0.005:
        return 'bear'
    else:
        return 'choppy'

# SUGGESTION 1: Dynamic gainers universe
def get_realtime_gainers(limit=30):
    try:
        url = "https://query1.finance.yahoo.com/v7/finance/screener/predefined/saved"
        params = {"scrIds": "day_gainers", "count": limit}
        r = requests.get(url, params=params, timeout=10)
        movers = []
        quotes = r.json()['finance']['result'][0]['quotes']
        for q in quotes:
            # SUGGESTION 2: Exclude penny/illiquid stocks here
            if 'symbol' in q and 'regularMarketPrice' in q and q['regularMarketPrice'] > 5 and q.get('averageDailyVolume3Month', 1e9) > 1e6:
                movers.append(q['symbol'])
        print(f"Realtime gainers from Yahoo: {movers}")
        return movers
    except Exception as e:
        print("Error fetching real-time gainers:", e)
        return []

def get_sector_candidates(market_status):
    if market_status == "bear":
        sector_stocks = []
        for stocks in DEFENSIVE_SECTORS.values():
            sector_stocks.extend(stocks)
        return sector_stocks
    return DEFAULT_CANDIDATES

# SUGGESTION 3: Entry signal filter (moving average + volume spike)
def filter_by_signals(symbols):
    filtered = []
    for symbol in symbols:
        try:
            bars = api.get_bars(symbol, '1Min', limit=15).df
            if len(bars) < 15:
                print(f"{symbol} skipped, not enough bar data.")
                continue
            avg_vol = bars['volume'][:10].mean()
            last_vol = bars['volume'].iloc[-1]
            price_ma10 = bars['close'][:10].mean()
            last_price = bars['close'].iloc[-1]
            if last_price > price_ma10 and last_vol > 1.2 * avg_vol:
                filtered.append(symbol)
            else:
                print(f"{symbol} filtered out: price/volume not strong. Last={last_price:.2f}, MA10={price_ma10:.2f}, Vol={last_vol}, AvgVol10={avg_vol:.0f}")
        except Exception as e:
            print(f"Signal filter error for {symbol}: {e}")
    print(f"Filtered candidates: {filtered}")
    return filtered

def get_relative_strength_movers(candidates, limit=20):
    spy_bars = api.get_bars('SPY', '1Min', limit=5).df
    spy_open = spy_bars['open'].iloc[0]
    spy_last = spy_bars['close'].iloc[-1]
    spy_gain = (spy_last - spy_open) / spy_open

    movers = []
    for symbol in candidates:
        try:
            bars = api.get_bars(symbol, '1Min', limit=5).df
            if len(bars) < 5:
                continue
            open_price = bars['open'].iloc[0]
            last_price = bars['close'].iloc[-1]
            gain = (last_price - open_price) / open_price
            relative_strength = gain - spy_gain
            movers.append((symbol, relative_strength, gain))
        except Exception:
            continue
    movers.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return [m[0] for m in movers[:limit]]

def buy_stock(symbol, dollars):
    try:
        last_quote = api.get_latest_quote(symbol)
        price = last_quote.ap if last_quote.ap > 0 else last_quote.bp
        qty = round(dollars / price, 4)
        if qty < 0.001:
            print(f"Not enough to buy any shares of {symbol}.")
            return
        api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='day')
        trade_log[symbol] = {"buy_price": price, "qty": qty}
        print(f"Buying {qty} shares of {symbol} at approx ${price:.2f}")
    except Exception as e:
        print(f"Buy error: {e}")

def sell_stock(symbol):
    try:
        position = api.get_position(symbol)
        sell_price = get_current_price(symbol)
        qty = float(position.qty)
        api.submit_order(symbol=symbol, qty=position.qty, side='sell', type='market', time_in_force='day')
        if symbol in trade_log:
            trade_log[symbol]["sell_price"] = sell_price
        print(f"Selling {position.qty} shares of {symbol}")
    except Exception as e:
        print(f"Sell error: {e}")

def get_open_positions():
    try:
        positions = api.list_positions()
        return {pos.symbol: float(pos.avg_entry_price) for pos in positions}
    except Exception as e:
        print(f"Position error: {e}")
        return {}

def get_current_price(symbol):
    try:
        quote = api.get_latest_quote(symbol)
        return quote.ap if quote.ap > 0 else quote.bp
    except Exception as e:
        print(f"Quote error: {e}")
        return 0

def is_near_close(buffer_minutes=15):
    now = datetime.now(eastern)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    buffer = timedelta(minutes=buffer_minutes)
    return now >= (market_close - buffer)

def sell_non_top_positions(top_movers):
    positions = get_open_positions()
    for symbol in positions.keys():
        if symbol not in top_movers:
            print(f"{symbol} is not a top mover, selling position...")
            sell_stock(symbol)
    time.sleep(2)

def export_trade_log(trade_log, filename='trades.csv'):
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['symbol', 'buy_price', 'sell_price', 'qty']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for symbol, record in trade_log.items():
                row = {'symbol': symbol}
                row.update({k: record.get(k, '') for k in fieldnames[1:]})
                writer.writerow(row)
        print(f"Trade log exported to {filename}")
    except Exception as e:
        print(f"Error exporting trade log: {e}")

def main():
    today = datetime.now(eastern)
    if today.strftime("%A") not in TRADING_DAYS:
        print(f"Not a trading day. Today is {today.strftime('%A')}")
        return

    print("Waiting for market open...")
    while not is_market_open():
        time.sleep(10)
    print("Market is open!")

    cash = STARTING_CASH
    current_cash = get_account_equity()
    if cash > current_cash:
        cash = current_cash

    print("Current account holdings: ", cash)
    losing_trades = 0
    day_trades = 0

    market_status = get_market_status()
    print(f"Market status is: {market_status}")
    if market_status == "bear":
        stop_loss = BEAR_STOP_LOSS
        take_profit = BEAR_TAKE_PROFIT
        print("Bear market detected. Using defensive sectors and tighter stops.")
    else:
        stop_loss = BULL_STOP_LOSS
        take_profit = BULL_TAKE_PROFIT

    # SUGGESTION 1: Use dynamic universe of gainers
    candidates = get_realtime_gainers(limit=POSITIONS * 8)
    if not candidates:
        print("Could not fetch real-time gainers, using sector/default universe.")
        candidates = get_sector_candidates(market_status)
    # SUGGESTION 2+3: filter by entry signals
    print(f"Filtering candidates for entry signals...")
    filtered_candidates = filter_by_signals(candidates)
    if not filtered_candidates:
        print("No filtered candidates passed entry signals, skipping trading.")
        return

    # Step 1: Filter for top relative strength movers
    top_movers = get_relative_strength_movers(filtered_candidates, limit=POSITIONS * 3)
    print(f"Relative strength movers: {top_movers}")

    # Sell anything not a top mover before buying
    sell_non_top_positions(top_movers)

    if not top_movers:
        print("No strong movers found. Staying in cash today.")
        return

    invest_per_stock = cash / POSITIONS
    picks = top_movers[:POSITIONS]
    print(f"Buying {picks}")

    for symbol in picks:
        buy_stock(symbol, invest_per_stock)
        time.sleep(2)

    buy_prices = {symbol: get_current_price(symbol) for symbol in picks}
    print("Monitoring for targets...")

    # Start keyboard listener for emergency actions
    listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
    listener_thread.start()

    # SUGGESTION 4: Add trailing stop dict
    trailing_high = {symbol: buy_prices[symbol] for symbol in picks}
    trailing_stop_pct = 0.02  # 2% trailing stop

    while day_trades < MAX_DAY_TRADES and is_market_open():

        if user_command["cmd"] == 's':
            print("User pressed 's' - Selling all positions and exiting...")
            positions = get_open_positions()
            for symbol in positions.keys():
                sell_stock(symbol)
            user_command["cmd"] = None
            break

        if user_command["cmd"] == 'r':
            print("User pressed 'r' - Rechecking all positions vs. new top movers...")
            print("Getting latest top movers...")
            # Always re-pull and re-filter universe on reset
            candidates = get_realtime_gainers(limit=POSITIONS * 8)
            filtered_candidates = filter_by_signals(candidates)
            top_movers = get_relative_strength_movers(filtered_candidates, limit=POSITIONS * 3)
            print(f"Got new top movers: {top_movers}")
            positions = get_open_positions()
            print(f"Current open positions: {positions.keys()}")
            for symbol in positions.keys():
                if symbol not in top_movers:
                    print(f"{symbol} is not a top mover, selling position...")
                    sell_stock(symbol)
            user_command["cmd"] = None
            print("Finished with reset, everything updated ...")
            print("Resuming monitoring ...")

        positions = get_open_positions()

        if not positions:
            print("No open positions. Exiting monitoring.")
            break

        for symbol, entry_price in positions.items():
            price = get_current_price(symbol)
            if price == 0:
                continue
            # SUGGESTION 4: Trailing stop
            if symbol in trailing_high:
                if price > trailing_high[symbol]:
                    trailing_high[symbol] = price
                trail_stop = trailing_high[symbol] * (1 - trailing_stop_pct)
                if price <= trail_stop:
                    print(f"{symbol} hit trailing stop, selling...")
                    sell_stock(symbol)
                    day_trades += 1
                    continue

            change = (price - entry_price) / entry_price
            if change <= stop_loss:
                print(f"{symbol} dropped {change*100:.2f}%, selling (stop loss)...")
                sell_stock(symbol)
                losing_trades += 1
                day_trades += 1
            elif change >= take_profit:
                print(f"{symbol} gained {change*100:.2f}%, selling (take profit)...")
                sell_stock(symbol)
                day_trades += 1

            if losing_trades >= MAX_LOSING_TRADES:
                print("Max losing trades hit. Stopping all trading for the day.")
                export_trade_log(trade_log)
                return

            if day_trades >= MAX_DAY_TRADES:
                print("Max day trades reached, stopping trading for the day.")
                export_trade_log(trade_log)
                return

        # Buy new top movers not in positions, still filtered
        positions = get_open_positions()
        current_symbols = set(positions.keys())
        new_picks = [s for s in top_movers if s not in current_symbols][:POSITIONS - len(current_symbols)]
        for symbol in new_picks:
            buy_stock(symbol, invest_per_stock)
            trailing_high[symbol] = get_current_price(symbol)
            time.sleep(2)
        # Auto-sell 15 min before close
        if is_near_close(buffer_minutes=15):
            print("It's 15 minutes before market close. Selling all positions.")
            positions = get_open_positions()
            for symbol in positions.keys():
                sell_stock(symbol)
            break
        time.sleep(30)

    print("Trading complete for the day.")
    print("\n--- TRADE SUMMARY ---")
    total_pnl = 0
    gainers = []
    for symbol, record in trade_log.items():
        if "buy_price" in record and "sell_price" in record:
            pnl = (record["sell_price"] - record["buy_price"]) * record["qty"]
            pct = ((record["sell_price"] - record["buy_price"]) / record["buy_price"]) * 100
            total_pnl += pnl
            gainers.append((symbol, pct, pnl))
            print(f"{symbol}: Buy ${record['buy_price']:.2f} → Sell ${record['sell_price']:.2f} | Qty: {record['qty']} | P/L: ${pnl:.2f} ({pct:.2f}%)")
    print(f"\nTotal Profit/Loss: ${total_pnl:.2f}")
    if gainers:
        gainers.sort(key=lambda x: x[1], reverse=True)
        print(f"\nBest performer: {gainers[0][0]} ({gainers[0][1]:.2f}%)")
        print(f"Worst performer: {gainers[-1][0]} ({gainers[-1][1]:.2f}%)")
    print("---------------------\n")

    # SUGGESTION 5: Export trade log for backtesting
    export_trade_log(trade_log)

if __name__ == "__main__":
    main()
