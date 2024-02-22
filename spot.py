from binance.client import Client
from binance import ThreadedWebsocketManager
from mysecrets import api_key_spot, api_secret_spot,api_key_spot_test, api_secret_spot_test
import pandas as pd
import time



# Testnet credentials:

client = Client(api_key_spot, api_secret_spot)

''' 
# Real credentials:

client = Client(api_key_spot, api_secret_spot)
'''

status = client.get_account_status()
print(status)

"""
# Ordem à mercado: 

order = client.create_order(
            symbol='BNBUSDT',
            side='BUY',  # 'BUY' para ordem de compra
            type='MARKET',  # 'MARKET' para ordem de mercado
            quantity= '0.1' # Quantidade desejada
        )

"""

""" 
# Código com laços de repetição para a execução de ordens market:

while True:
    # Obtenha o preço atual do par de moedas
    ticker = client.get_ticker(symbol='BNBUSDT')
    current_price = float(ticker['lastPrice'])
    target_price = 310

    # Verifique se o preço atingiu a condição desejada
    if current_price >= target_price:
        # Abra uma ordem de mercado
        order = client.create_order(
            symbol='BNBUSDT',
            side='BUY',  # 'BUY' para ordem de compra
            type='MARKET',  # 'MARKET' para ordem de mercado
            quantity= '0.1' # Quantidade desejada
        )
        print(f"Ordem aberta! Preço atingido: {current_price}")
        break

    # Aguarde um tempo antes de verificar novamente
    time.sleep(60)  # Aguarde 60 segundos (você pode ajustar o intervalo conforme necessário)
"""

"""
# Robo de monitoramento de preço para compra e venda:

twm = ThreadedWebsocketManager()
twm.start()

def simple_bot(msg):
    '''define how to process incoming WebStocket messages'''
    time = pd.to_datetime(msg["E"], unit = "ms")
    price = float(msg["c"])
    print("Time {}: | Price: {}".format(time, price))

    if int(price) > 1.100:
        order = client.create_order(symbol="PERPUSDT", side="BUY", type="MARKET", quantity= 5)
        print("\n" + 50 * "-")
        print("Buy {} PERP for {} USDT".format(order["executedQty"], order["cummulativeQuoteQty"]))
        print(50 * "-" + "\n")

        twm.stop()

twm.start_symbol_miniticker_socket(callback=simple_bot, symbol="PERPUSDT")
twm.join()

"""