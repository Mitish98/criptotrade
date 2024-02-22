from binance.client import Client
import numpy as np
import pandas as pd
import requests
import time
import threading
from mysecrets import api_key_spot, api_secret_spot

client = Client(api_key_spot, api_secret_spot)

def get_binance_server_time():
    url = "https://api.binance.com/api/v3/time"
    response = requests.get(url)
    server_time = response.json()['serverTime']
    return server_time

symbols = ['ETHUSDT', 'BNBUSDT', 'SOLUSDT']
amounts = {'ETHUSDT': '0.02', 'BNBUSDT': '0.03', 'SOLUSDT': '1'}

compra_realizada = False
ordens_abertas = {}  # Usaremos um dicionário para rastrear as ordens abertas

def get_current_price(symbol):
    ticker = client.futures_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

def get_price_history(symbol, interval, limit):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    closes = [float(kline[4]) for kline in klines]
    return closes

def calculate_bollinger_bands(prices, window_size, num_std_dev=2):
    sma = prices.rolling(window=window_size).mean()
    std_dev = prices.rolling(window=window_size).std()
    upper_band = sma + (num_std_dev * std_dev)
    lower_band = sma - (num_std_dev * std_dev)
    return upper_band, sma, lower_band

def place_market_buy_order(symbol, quantity):
    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity
    )
    return order['orderId']

def place_market_sell_order(symbol, quantity):
    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity
    )
    return order['orderId']

def verificar_margens_e_fechar(symbol, quantidade_comprada, preco_compra):
    margem_lucro = 1.004
    stop_loss = 0.996

    preco_alvo = preco_compra * margem_lucro
    preco_stop_loss = preco_compra * stop_loss

    while True:
        preco_atual = get_current_price(symbol)

        if preco_atual >= preco_alvo or preco_atual <= preco_stop_loss:
            print(f"Preço atingiu a margem de lucro ou stop loss. Fechando posição...")
            place_market_sell_order(symbol, quantidade_comprada)
            break

        time.sleep(5)

def scalping_strategy(symbol, amount):
    global compra_realizada, ordem_aberta
    
    print(f"Iniciando estratégia de scalping para {symbol} no timeframe de 1 minuto...")
    
    compra_realizada = False
    ordem_aberta = None
    
    # Obtenha dados suficientes para calcular as médias móveis e as Bollinger Bands
    prices = get_price_history(symbol, Client.KLINE_INTERVAL_1MINUTE, limit=100)  # Adicione o valor adequado para 'limit'
    
    while True:
        try:
            if ordem_aberta:
                verificar_margens_e_fechar(symbol, amount, get_current_price(symbol))
                break

            current_price = get_current_price(symbol)

            # Calcule as Bollinger Bands
            upper_band, middle_band, lower_band = calculate_bollinger_bands(pd.Series(prices), window_size=21)

            print(f"Preço atual ({symbol}): {current_price} | Banda Superior: {upper_band.iloc[-1]} | Banda Inferior: {lower_band.iloc[-1]}")

            if current_price <= lower_band.iloc[-1]:
                print("Sinal de compra - Preço rompeu a Banda Inferior! Executando ordem de compra...")
                ordem_aberta = place_market_buy_order(symbol, amount)
                print(f"Ordem de compra executada ({symbol}): {ordem_aberta} - Preço atual: {current_price}")
                compra_realizada = True

            # Atualize o histórico de preços com o preço atual
            prices.append(current_price)

            time.sleep(5)

        except Exception as e:
            print(f"Erro ({symbol}): {e}")
            time.sleep(5)

# Execute a estratégia para cada par usando threads separadas
threads = []
for symbol in symbols:
    thread = threading.Thread(target=scalping_strategy, args=(symbol, amounts[symbol]))
    threads.append(thread)
    thread.start()

# Aguarde que todas as threads sejam concluídas
for thread in threads:
    thread.join()
