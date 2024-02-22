## Funcionalidades: 
## - Análises de preço e análise de tickers 
## - Envio automático de ordem com base em estratégias
## - Gerenciamento de risco automático com profit e stop-loss
## - Trade automático de multiplas moedas
## - Relatório de desempenho

## Problemas: 

## - O mercado não está sendo rastreado em tempo real 
## - As médias não coincidem com os calculos da Binance
## - O robo não identifica o cruzamento de média corretamente 
## - Os relatórios gerados não estão formatados e salvos corretamente

import pandas as pd
from binance.client import Client
from mysecrets import api_key_spot, api_secret_spot
from datetime import datetime
import numpy as np
import time
from threading import Thread

client = Client(api_key_spot, api_secret_spot)

# Dicionários para rastrear informações
saldo_inicial = {}
lucro_total = {}
prejuizo_total = {}
taxa_acertos_total = {}
taxa_erros_total = {}


def calcular_taxas_totais(symbol, taxa_acertos, taxa_erros):
    taxa_acertos_total[symbol] = taxa_acertos_total.get(symbol, 0) + taxa_acertos
    taxa_erros_total[symbol] = taxa_erros_total.get(symbol, 0) + taxa_erros

def escrever_relatorio(symbol, quantidade, preco_compra, lucro_prejuizo, status, taxa_acertos, taxa_erros):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_operacao = f"{symbol}_{data_hora}"

    saldo_final = saldo_inicial.get(symbol, 0) + lucro_prejuizo
    lucro_total[symbol] = lucro_total.get(symbol, 0) + max(0, lucro_prejuizo)
    prejuizo_total[symbol] = prejuizo_total.get(symbol, 0) + max(0, -lucro_prejuizo)

    dados_operacao = {
        'Data_Hora': [data_hora],
        'ID_Operacao': [id_operacao],
        'Quantidade': [quantidade],
        'Preco_Compra': [preco_compra],
        'Lucro_Prejuizo': [lucro_prejuizo],
        'Status': [status],
        'Taxa_Acertos': [taxa_acertos],
        'Taxa_Erros': [taxa_erros],
        'Saldo_Inicial': [saldo_inicial.get(symbol, 0)],
        'Saldo_Final': [saldo_final],
        'Lucro_Total': [lucro_total[symbol]],
        'Prejuizo_Total': [prejuizo_total[symbol]]
    }

    df_operacao = pd.DataFrame(dados_operacao)
    print(df_operacao)
    
    calcular_taxas_totais(symbol, taxa_acertos, taxa_erros)
    saldo_inicial[symbol] = get_current_price(symbol)

def get_current_price(symbol):
    ticker = client.futures_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

def get_price_history(symbol, interval, limit):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    closes = [float(kline[4]) for kline in klines]
    return closes

def calculate_moving_averages(prices, fast_period, slow_period):
    ma_fast = np.mean(prices[-fast_period:])
    ma_slow = np.mean(prices[-slow_period:])
    return ma_fast, ma_slow

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

        if preco_atual >= preco_alvo:
            print(f"Preço atingiu a margem de lucro. Fechando posição...")
            place_market_sell_order(symbol, quantidade_comprada)
            lucro_prejuizo = preco_atual - preco_compra
            escrever_relatorio(symbol, quantidade_comprada, preco_compra, lucro_prejuizo, "Posição Ganha", 1, 0)
            break

        elif preco_atual <= preco_stop_loss:
            print(f"Preço atingiu o stop loss. Fechando posição...")
            place_market_sell_order(symbol, quantidade_comprada)
            lucro_prejuizo = preco_atual - preco_compra
            escrever_relatorio(symbol, quantidade_comprada, preco_compra, lucro_prejuizo, "Posição Perdida", 0, 1)
            break

        time.sleep(5)

def scalping_strategy(symbol, amount, compra_realizada, ordens_abertas):
    print(f"Iniciando estratégia de scalping para {symbol} no timeframe de 1 minuto...")

    compra_realizada[symbol] = False
    ordens_abertas[symbol] = None

    # Obtenha dados suficientes para calcular as médias móveis
    ma_fast_period = 21
    ma_slow_period = 50
    prices = get_price_history(symbol, Client.KLINE_INTERVAL_1MINUTE, ma_slow_period + ma_fast_period)

    while True:
        try:
            if ordens_abertas.get(symbol):
                verificar_margens_e_fechar(symbol, amount, get_current_price(symbol))
                break

            current_price = get_current_price(symbol)

            # Atualize o histórico de preços com o preço atual
            prices.append(current_price)

            if len(prices) >= ma_slow_period + ma_fast_period:
                ma_fast, ma_slow = calculate_moving_averages(prices, ma_fast_period, ma_slow_period)

                print(f"Preço atual ({symbol}): {current_price} | Média Móvel Rápida: {ma_fast} | Média Móvel Lenta: {ma_slow}")

                if ma_fast > ma_slow and prices[-2] <= ma_slow and not compra_realizada.get(symbol):
                    print("Cruzamento detectado! Executando ordem de compra...")
                    print(f"Preço-alvo: {current_price * 1.006} | Stop-loss: {current_price * 0.995}")
                    ordens_abertas[symbol] = place_market_buy_order(symbol, amount)
                    print(f"Ordem de compra executada ({symbol}): {ordens_abertas[symbol]} - Preço atual: {current_price}")
                    compra_realizada[symbol] = True

            time.sleep(5)

        except Exception as e:
            print(f"Erro ({symbol}): {e}")
            time.sleep(5)

# Função para executar a estratégia para um par
def run_strategy_for_symbol(symbol, amount, compra_realizada, ordens_abertas):
    while True:
        scalping_strategy(symbol, amount, compra_realizada, ordens_abertas)
        # Aguarde um intervalo de tempo antes de iniciar uma nova iteração
        time.sleep(60)  # por exemplo, espera 1 minuto antes de reiniciar a estratégia

# Execute a estratégia para cada par usando threads
symbols = ['ETHUSDT', 'BNBUSDT', 'TIAUSDT', 'MINAUSDT', 'MANTAUSDT', 'ETCUSDT', 'TRBUSDT']
amounts = {'ETHUSDT': '0.02', 'BNBUSDT': '0.03', 'TIAUSDT': '1', 'MINAUSDT': '5', 'MANTAUSDT': '2.3', 'ETCUSDT': '1', 'TRBUSDT': '0.1'}

compra_realizada = {}
ordens_abertas = {}

threads = []
for symbol in symbols:
    thread = Thread(target=run_strategy_for_symbol, args=(symbol, amounts[symbol], compra_realizada, ordens_abertas))
    threads.append(thread)
    thread.start()

# Aguarde todas as threads terminarem
for thread in threads:
    thread.join()
