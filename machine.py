from binance.client import Client
from binance import AsyncClient, BinanceSocketManager
from websockets.exceptions import ConnectionClosedError
from mysecrets import api_key_spot, api_secret_spot
import pandas as pd
import asyncio
import time

client = Client(api_key_spot, api_secret_spot)

status = client.get_account_status()
print(status)

# Informações gerais  
exchange = client.get_exchange_info()
limit_API = client.get_exchange_info()["rateLimits"]


coins = client.get_all_tickers()
dfCoins = pd.DataFrame(coins)
dfCoins = dfCoins[dfCoins.symbol.str.contains('USDT')]
print(dfCoins)


last24 = client.get_ticker(symbol='BNBUSDT')
price_change = last24['priceChange']
print(f"A mudança de preço em 24h no BNBUSDT foi de $ {price_change}")

open_price = float(last24["openPrice"])
print(f"O preço de abertura do BNB nas últimas 24h foi de $ {open_price}")

high_price = float(last24["highPrice"])
print(f"O preço mais alto do BNB nas últimas 24h foi de $ {high_price}")

low_price = float(last24["lowPrice"])
print(f"O preço mais baixo do BNB nas últimas 24h foi de $ {low_price}")

close_price = float(last24["lastPrice"])
print(f"O preço de fechamento do BNB das últimas 24h foi de $ {low_price}")


tickers = client.get_orderbook_tickers()
# Informações de symbols
ticker = client.get_symbol_ticker(symbol = 'BNBUSDT')
ticker = ticker['price']
print(f"O preço do BNB está cotado em $ {ticker}")

"""
# Teste para a coleta de informações das coins

symbol = client.get_symbol_info('BNBUSDT')

depth = client.get_order_book(symbol='BNBUSDT')

candles = client.get_klines(symbol='BNBUSDT', interval=Client.KLINE_INTERVAL_30MINUTE)

    # fetch 1 minute klines for the last day up until now
klines = client.get_historical_klines("BNBUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

    # fetch 30 minute klines for the last month of 2017
klines = client.get_historical_klines("BNBUSDT", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

    # fetch weekly klines since it listed
klines = client.get_historical_klines("BNBUSDT", Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017")
"""

avg_price = float(client.get_avg_price(symbol='BNBUSDT')["price"])
print(f"O preço médio do BNB está cotado em {avg_price} USDT")

fee = client.get_trade_fee(symbol='BNBUSDT')
print(f"As informações sobre taxas no BNB são: {fee}")

timestamp = client._get_earliest_valid_timestamp(symbol = "BNBUSDT", interval="1d")

bars = client.get_historical_klines(symbol="BNBUSDT", interval="1d", start_str=timestamp, limit=1000)
dfBars = pd.DataFrame(bars)
for column in dfBars.columns:
    dfBars[column] = pd.to_numeric(dfBars[column], errors = "coerce")

"""
# Teste aula 
https://www.udemy.com/course/cryptocurrency-algorithmic-trading-with-python-and-binance/learn/lecture/28485202#overview
Como coletar dados históricos de moedas em um timeframe específico? 

def get_history(symbol, interval, start, end = None):
    bars = client.get_historical_klines(symbol = symbol,interval = interval, start_str= start, end_str=end, limit=1000)
    dfBars = pd.DataFrame(bars)
    dfBars["Date"] = pd.to_datetime(dfBars.iloc[:,0], unit= "ms")
    dfBars.columns = ["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote Asset", "Number of trades", "Taker buy base asset", "Taker buy quote asset", "Ignore", "Date"]
    dfBars = dfBars[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    dfBars.set_index("Date", inplace=True)
    for column in dfBars.columns:
        dfBars[column] = pd.to_numeric(dfBars[column], errors="coerce")

    print(dfBars)

    return dfBars
"""

def stream_data(msg):
    '''Define how to process incoming WebSocket messages'''
    time = pd.to_datetime(msg["E"], unit = "ms") ## Transform event in date
    price = msg["c"] ## Select what column you want here (open, high, low, close, volume)
    print("Time: {} | Price: {}".format(time, price)) ## Or just 'print(msg)' to get all informations about the coin

async def main(loop_limit=10):
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.symbol_miniticker_socket(symbol="BTCUSDT")                                ## Streams miniticker data for symbols

    async with ts as tscm:                                                            ## "e" = Event type
        loop_count = 0                                                                ## "E" = Event time
        while True:                                                                   ## "s" = Symbol
            msg = await tscm.recv()                                                   ## "c" = Close price
            stream_data(msg)                                                          ## "o" = Open price
            loop_count += 1                                                           ## "h" = High price
            if loop_count >= loop_limit:                                              ## "l" = Low price
                break                                                                 ## "v" = Volume
                                                                                      ## "q" = Quote assets volume
                                                                                      
# Executa a função principal
if __name__ == "__main__":
    import asyncio

    # Configura e executa o loop de eventos assíncronos
    loop_limit = 3  # Defina o número desejado de loops
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop_limit))



df = pd.DataFrame(columns = ["Open", "High", "Low", "Close", "Volume", "Complete"])

def stream_candles(msg):
    '''Define how to process incoming WebSocket messages from the candlestick data'''
    event_time = pd.to_datetime(msg["E"], unit="ms")
    start_time = pd.to_datetime(msg["k"]["t"], unit="ms")
    first = float(msg["k"]["o"])
    high = float(msg["k"]["h"])
    low = float(msg["k"]["l"])
    close = float(msg["k"]["c"])
    volume = float(msg["k"]["v"])
    complete = msg["k"]["x"]

    df.loc[start_time] = [first, high, low, close, volume, complete]

"""
# Objective: Trying to get a stream candle for BTCUSDT in a especify interval 
# Trouble: i can't get more than 1 clandle
# Troubleshooting: get a defined number of candles for all timeframes

async def candles():
    client = await AsyncClient.create()
    bsm = BinanceSocketManager(client)
    tsm = bsm.kline_socket(symbol="BTCUSDT", interval="1m")

    async with tsm as tscm:
      
        for _ in range(loop_limit):
            res = await tscm.recv()
            stream_candles(res)
              

      # Print DataFrame inside the candles function
    await client.close_connection()

# Executa a função principal
if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(candles())

print(df)

"""