from dotenv import load_dotenv
import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import os

load_dotenv()

def analyze (ticker, tf):
    exchange = ccxt.binanceusdm()
    bars = exchange.fetch_ohlcv(ticker, timeframe = tf, limit = 500)
    df = pd.DataFrame(bars, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit = 'ms')
    counter = [*range(0, df.shape[0])]

    ema12 = df.ta.ema(12)
    ema48 = df.ta.ema(48)
    ema192 = df.ta.ema(192)
    EMA = pd.concat([ema12, ema48, ema192], axis = 1)

    df = pd.concat([df, EMA], axis = 1)
    uplimit = []
    n = 0

    try:
        ema = df['EMA_192']
    except KeyError:
        print('There are not enough candles to analyze in {} timeframe.'.format((tf)))
        return

    for n in counter:
        sum = (float((0.001*(ema[n]))) + float(ema[n]))
        uplimit.append(sum)

    up_limit = pd.DataFrame(uplimit, columns = ['up_rnge'])
    lowlimit = []
    n = 0

    for n in counter:
        minus = (float((ema[n])) - float((0.001*(ema[n]))))
        lowlimit.append(minus)

    low_limit = pd.DataFrame(lowlimit, columns = ['low_rnge'])
    rnge = pd.concat([up_limit, low_limit], axis = 1)
    df = pd.concat([df, rnge], axis = 1)

    last_row = df.iloc[-2]

    print(last_row)

    isSentMessage = False

    if (last_row['low'] < last_row['up_rnge']) and (last_row['high'] > last_row['low_rnge']):
        message = 'TimeFrame: {}\nOpen: ${}\nClose: ${}\nEMA 192: ${}'.format((tf), (last_row['open']), (last_row['close']), (last_row['EMA_192']))

        print(message)

        payload = {
          'username': ('{}-PERP'.format(ticker)),
          'content': message
        }

        requests.post(os.getenv('WEBHOOK_URL'), json = payload)
        isSentMessage = True

    if (isSentMessage == False) and (
      last_row['low'] < last_row['up_rnge']) and (last_row['high'] > last_row['low_rnge']
    ):
        message = 'TimeFrame: {}\nOpen: ${}\nClose: ${}\nEMA 192: ${}'.format((tf), (last_row['open']), (last_row['close']), (last_row['EMA_192']))

        print(message)

        payload = {
          'username': ('{}-PERP'.format(ticker)),
          'content': message
        }

        requests.post(os.getenv('WEBHOOK_URL'), json = payload)

ticker_sym = pd.read_csv('./ticker.csv', header = None)
ticker_sym.columns = ['symbol']
timeframe = ['1h', '4h', '12h', '1d']

def run():
    z = 0
    lent = len(timeframe)
    lens = len(ticker_sym)
    ticker = ''
    tf = ''

    while z < lent:
        tf = str(timeframe[z])

        print(tf)

        c = 0

        while c < lens:
            ticker = (ticker_sym['symbol'][c])

            print(ticker)

            analyze(ticker, tf)

            c = c + 1

        z = z + 1

run()
