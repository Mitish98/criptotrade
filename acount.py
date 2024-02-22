# Importações
from binance.client import Client
from mysecrets import api_key_acount, api_secret_acount
import time
import pandas as pd

# Conexão

client = Client(api_key_acount, api_secret_acount)

status = client.get_account_status()
time_res = client.get_server_time()
print(status)

# Informações gerais  

acount = client.get_account()
snapshot = client.get_account_snapshot(type='SPOT')
snapshot = pd.json_normalize(snapshot["snapshotVos"])
print(f"Snapshot {snapshot}")
    
    # Ver os salos dos ativos
lista_ativos = acount["balances"]
print("Meus ativos:")
for ativo in lista_ativos:
    if float(ativo["free"]) > 0:
        dfAtivo = pd.DataFrame(ativo, index=[0])
        print(dfAtivo)

trades = client.get_my_trades(symbol="BNBUSDT")
dfTrades = pd.DataFrame(trades)
print("Trades:\n", dfTrades)














    



