import ccxt
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

exchange = ccxt.binance()

def calculate_ema(data, period):
    alpha = 2 / (period + 1)
    ema = [data[0]]
    for i in range(1, len(data)):
        ema.append(alpha * data[i] + (1 - alpha) * ema[-1])
    return ema[-1]

def check_ema_trend(pair, timeframe):
    ohlcv = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=500)
    close_prices = [candle[4] for candle in ohlcv]

    ema10 = calculate_ema(close_prices, 10)
    ema20 = calculate_ema(close_prices, 20)
    ema40 = calculate_ema(close_prices, 40)
    ema60 = calculate_ema(close_prices, 60)
    ema120 = calculate_ema(close_prices, 120)
    ema250 = calculate_ema(close_prices, 250)

    if ema10 > ema20 > ema40 > ema60 > ema120 > ema250:
        return "符合特定趋势"
    else:
        return "不符合特定趋势"

def send_email(subject, message):
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECEIVER_EMAIL')
    password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

def monitor_all_pairs():
    markets = exchange.load_markets()
    for symbol in markets:
        for timeframe in ['15m', '1h']:
            trend = check_ema_trend(symbol, timeframe)
            if trend == "符合特定趋势":
                send_email(f"{symbol} {timeframe} EMA 趋势警报", f"{symbol}在{timeframe}时间框架下符合特定 EMA 趋势！")

if __name__ == '__main__':
    monitor_all_pairs()
