import requests, json as j, pandas as pd, time
import datetime
from stockstats import StockDataFrame as Sdf

def log(text, action):
    f = open("rsi.txt", action)
    f.write(str(datetime.datetime.now()) + " " + text + '\n')
    print(str(datetime.datetime.now()) + text)
    f.close()

def sma(serie,ruedas,nombreColumna):
    rta=pd.DataFrame({nombreColumna:[]})
    i = 0
    for valor in serie:
        if(i >= ruedas):
            promedio = sum(serie[i-ruedas+1:i+1])/ruedas
            rta.loc[i] = promedio
        i = i+1
    return rta


def action(rsi,cruce, pos,price,sl):
    if (pos=="wait" and rsi > 50 and cruce>1):
        pos = "hold"
        sl = price * 0.99
        entryprice = price
        log("buy @ " + str(price) + " rsi " + str(rsi) + " stop loss " + str(sl), "a")
    elif(pos=="hold" and price <= sl):
        result = entryprice - price
        sellstopprice = price
        log("sell stop loss @ " + str(price) + " rsi " + str(rsi) + " result " + str(result), "a")
        pos = "wait"
    elif(pos=="hold" and rsi > 70):
        result = entryprice - price
        log("sell win trade @ " + str(price) + " rsi " + str(rsi) + " result " + str(result), "a")
        pos = "wait"
    else:
        pos = pos

    return pos

log("inicio ejecucion ", "w")
pos = "wait"
sl = 0
entryprice=0
exitprice=0
nRapida=9
nLenta=14

while True:
    url = "https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=1000&e=bittrex"
    json = j.loads(requests.get(url = url).text)
    df = pd.DataFrame(json['Data']['Data']).dropna()

    #MEDIAS MOVILES
    rapidas = sma(df['close'],nRapida,"rapida")
    lentas = sma(df['close'],nLenta,"lenta")

    tabla = rapidas.join(lentas).join(df['close']).dropna().reset_index()
    cruce = tabla['rapida'].iloc[-1] / tabla['lenta'].iloc[-1]

    print("cruce : " + str(cruce))

    #RSI
    stock_df = Sdf.retype(df)

    rsi = stock_df["rsi_14"][1000]
    price = df["close"][1000]

    pos = action(rsi, cruce, pos, price,sl)


    print("price : " + str(price) + " rsi: " + str(rsi) + " " + pos)


    time.sleep(10)