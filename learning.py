import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from binance.client import Client
from datetime import datetime

# Substitua 'SEU_API_KEY' e 'SUA_API_SECRET' pelos valores reais da sua conta Binance
client = Client(api_key='SEU_API_KEY', api_secret='SUA_API_SECRET')

# Especifica o par de criptomoedas e o intervalo de tempo desejado
symbol = 'BTCUSDT'
interval = '1h'

# Obtém dados históricos da Binance
klines = client.get_klines(symbol=symbol, interval=interval)

# Converte os dados para DataFrame
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

# Ajusta os tipos de dados
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['close'] = pd.to_numeric(df['close'])

# Adiciona uma coluna de retorno (pode ser ajustada para atender ao seu objetivo)
df['return'] = df['close'].pct_change() * 100

# Remove valores nulos
df = df.dropna()

# Especifica as características (features) e o alvo
X = df[['open', 'high', 'low', 'volume']]
y = df['return']

# Divide os dados em conjuntos de treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Cria o modelo de regressão linear
model = LinearRegression()

# Treina o modelo
model.fit(X_train, y_train)

# Faz previsões no conjunto de teste
predictions = model.predict(X_test)

# Avalia o desempenho
accuracy = model.score(X_test, y_test)
print(f'Acurácia do modelo: {accuracy}')

# Visualiza os resultados
plt.scatter(X_test['close'], y_test, color='black')
plt.plot(X_test['close'], predictions, color='blue', linewidth=3)
plt.xlabel('Preço de Fechamento')
plt.ylabel('Retorno (%)')
plt.title('Regressão Linear para Prever Retorno de Preços')
plt.show()
