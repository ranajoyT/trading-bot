import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from telebot import TeleBot

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = '7741292617:AAHo9Vr9Y1wwGXuWLqvjtXm92PA1_EoavrM'
TELEGRAM_CHAT_ID = '6975094896'
INTERVAL = '15m'  # You can use 5m, 15m, 1h etc.
LOOKBACK = 20  # Number of candles to look back for pattern
SYMBOLS = {
    'NIFTY_AUTO': 'NSE:NIFTYAUTO',
    'NIFTY_BANK': 'NSE:BANKNIFTY'
}

bot = TeleBot(TELEGRAM_BOT_TOKEN)

# === FETCH CANDLESTICK DATA ===
def fetch_candles(symbol):
    url = f"https://priceapi.moneycontrol.com/techCharts/indianMarket/stock/history?symbol={symbol.split(':')[1]}&resolution={INTERVAL}&from={(int(time.time()) - 3600*24)}&to={int(time.time())}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    df = pd.DataFrame({
        'time': [datetime.fromtimestamp(x) for x in data['t']],
        'open': data['o'],
        'high': data['h'],
        'low': data['l'],
        'close': data['c'],
        'volume': data['v'],
    })
    return df

# === DETECT HIGHER HIGH / HIGHER LOW ===
def detect_trend(df):
    highs = df['high'].tail(LOOKBACK)
    lows = df['low'].tail(LOOKBACK)

    higher_highs = all(x < y for x, y in zip(highs, highs[1:]))
    higher_lows = all(x < y for x, y in zip(lows, lows[1:]))

    if higher_highs and higher_lows:
        return "Uptrend: Higher Highs & Higher Lows"
    elif higher_highs:
        return "Higher Highs forming"
    elif higher_lows:
        return "Higher Lows forming"
    return None

# === ANALYZE AND NOTIFY ===
def analyze_and_notify():
    for name, symbol in SYMBOLS.items():
        df = fetch_candles(symbol)
        if df is None or df.empty:
            continue

        trend = detect_trend(df)
        if trend:
            message = f"\U0001F4C8 *{name}* ({symbol})\nTrend Detected: *{trend}*\nLatest Close: {df['close'].iloc[-1]}\nTime: {df['time'].iloc[-1].strftime('%Y-%m-%d %H:%M')}"
            bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode='Markdown')

# === MAIN LOOP ===
if __name__ == '__main__':
    while True:
        try:
            analyze_and_notify()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(900)  # Run every 15 minutes
