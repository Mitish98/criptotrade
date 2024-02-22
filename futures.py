## Didi Aguiar - Agulhada

from binance.client import Client
from mysecrets import api_key_spot, api_secret_spot
import pandas as pd


client = Client(api_key_spot, api_secret_spot)

class analytics:

    candles = client.get_klines(symbol='BTCUSDT', interval='4h', limit=10) ## Este trecho específico está solicitando os últimos 10 candles (velas) de uma hora (intervalo '1h') para o par de negociação 'BTCUSDT'.
    df_candles = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume'])
    df_candles[['open', 'high', 'low', 'close', 'volume']] = df_candles[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)
    print(df_candles)

    ## Saída: Lista com as informações dos 10 últimos candles
    """
    Timestamp em milissegundos (por exemplo, 1708340400000).
    Preço de abertura ('open').
    Preço mais alto ('high').
    Preço mais baixo ('low').
    Preço de fechamento ('close').
    Volume negociado.
    Timestamp final do candle.
    Volume em moeda de cotação ('quote asset volume').
    Número de negócios.
    Taker buy base asset volume.
    Taker buy quote asset volume.
    """

    # Método para acessar uma informação específica em todos os candles
    volumes = [candle[5] for candle in candles]
    print("Volumes de todos os candles:", volumes)

    # Metódo para acessar os dados de um candle específico:
    last_candle = candles[-1]
    print("Último candle:", last_candle)

    # Método para acessar uma informação específica de um determinado candle
    vol_candle_one = candles[0][5]
    print("Volume do primeiro candle:", vol_candle_one)

class calculate:

    analytics.df_candles['SMA21'] = analytics.df_candles['close'].rolling(window=21).mean()
    print("Move Average 21: ", analytics.df_candles['SMA21'])

    # Calcula o desvio padrão de 21 períodos para as Bandas de Bollinger
    analytics.df_candles['std_dev'] = analytics.df_candles['close'].rolling(window=21).std()

    # Calcula as Bandas de Bollinger
    analytics.df_candles['upper_band'] = analytics.df_candles['SMA21'] + (2 * analytics.df_candles['std_dev'])
    print("Upper band: ", analytics.df_candles['upper_band'])
    analytics.df_candles['lower_band'] = analytics.df_candles['SMA21'] - (2 * analytics.df_candles['std_dev'])
    print("Lower band: ", analytics.df_candles['lower_band'])

    ## Estocástico lento
    k_period = 14
    d_period = 3
    analytics.df_candles['stoch_k'] = (analytics.df_candles['close'] - analytics.df_candles['low'].rolling(window=k_period).min()) / (analytics.df_candles['high'].rolling(window=k_period).max() - analytics.df_candles['low'].rolling(window=k_period).min()) * 100
    analytics.df_candles['stoch_d'] = analytics.df_candles['stoch_k'].rolling(window=d_period).mean()
    print("Estocástico superior: ", analytics.df_candles['stoch_k'])
    print("Estocástico inferior: ", analytics.df_candles['stoch_d'])

class strategy:
    


    



