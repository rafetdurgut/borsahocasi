import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import talib
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
pd.options.plotting.backend = "plotly"
from binance.client import Client
from Utils import *
import json
import websocket
import asyncio
client = Client('qrghbOB5VJ2zeDUu1D690M14238Jpd2ScMr4Y8t4UPe7COnerc26peVDIjCTOoPT', 'VkAG3ioH9yIw7WvVEvChCCOeGrUdbi83jRzNgnWsroVl4SDBXOAiTNhoDCEnpTHL')

class EqSignal:
  def __init__(self, indicators, buyCriteria, sellCriteria):
    self.signs = pd.concat([np.sign(ind.points.diff()).dropna().eq(1) for ind in indicators], join='inner', axis=1).dropna()
    self.signs.dropna(inplace=True)
    self.buyPoints = self.signs[self.signs.eq(buyCriteria,axis=1).all(1)][0]
    self.islem = False
    if len(self.buyPoints)>0:
      self.islem = True
      self.side = 1
    self.sellPoints = self.signs[self.signs.eq(sellCriteria,axis=1).all(1)][0]

    if len(self.sellPoints)>0:
      self.islem = True
      self.side = -1

from datetime import datetime,timedelta

kasa = 100
def buy(stockCode,alisTutari):
    alisHisseMiktar = int((kasa*0.2)/alisTutari)
    alisTutari = alisHisseMiktar*alisTutari
    komisyon = alisTutari*0.001
    if kasa > (alisTutari+komisyon) and alisHisseMiktar>0:
        oncekiPortfoyDegeri = portfoy.loc[stockCode].amount * portfoy.loc[stockCode].ort
        komisyon = alisTutari*0.002
        portfoy.amount.loc[stockCode] += alisHisseMiktar
        portfoy.ort.loc[stockCode] = (oncekiPortfoyDegeri + alisTutari)/portfoy.loc[stockCode].amount
        toplamKomisyon += komisyon
        kasa -= alisHisseMiktar * alisTutari + komisyon

def sell(stockCode,satisTutari):
    satisAdet = int(portfoy.loc[stockCode].amount)
    if satisAdet>0:
        satisTutari = satisAdet * satisTutari
        komisyon = satisTutari*0.002
        kasa += (satisTutari-komisyon)
        portfoy.amount.loc[stockCode] -= satisAdet
#Get Stock List
tickers = client.get_ticker()
tickers = pd.DataFrame(tickers)
stockList = tickers[tickers['symbol'].str.endswith('USDT')].sort_values('volume',ascending=False)[0:50]
stockList = pd.DataFrame(stockList)
stockList = stockList.symbol

portfoy = pd.DataFrame(index=stockList.unique(),columns=['amount','ort'])
portfoy['amount'] = 0
portfoy['ort'] = 0

veri = pd.DataFrame(columns =['stock', 'date', 'Close', 'Low'])
veri.set_index('stock')  

for s in stockList:
    gen = client.get_historical_klines(s, Client.KLINE_INTERVAL_5MINUTE, "15 hours ago UTC")
    raw_data = pd.DataFrame(gen, dtype=float, columns = ('date',
                                                                      'Open',
                                                                      'High',
                                                                      'Low',
                                                                      'Close',
                                                                      'Volume',
                                                                      'Close time',
                                                                      'Quote asset volume',
                                                                      'Number of trades',
                                                                      'Taker buy base asset volume',
                                                                      'Taker buy quote asset volume',
                                                                      'Ignore'))
    raw_data['date'] = pd.to_datetime(raw_data['date'],unit='ms')
    raw_data['stock'] = s
    veri = pd.concat([veri, raw_data[['stock','date','Close', 'Low']]], ignore_index=True)





PERIOD=1

def on_open(ws):
    print('open')

def on_message(ws,message):
    global veri

    json_message = json.loads(message) 
    candle = json_message['data']['k']
    is_candle_closed = candle['x']
    volume = candle['v']  

    if is_candle_closed:
        print("candle closed")
        low = float(candle['l'])
        close = float(candle['c'] ) 
        stock = json_message['data']['s']  
        date = datetime.fromtimestamp(float(json_message['data']['E'])/1000)
        veri.loc[date] = [ stock, date, close, low ]
        #Calculate indicator
        #12 saatlik veri geldiyse
        if len(veri[veri.stock==stock]) >= PERIOD:
            print(len(veri[veri.stock==stock]))
            veri.set_index('date', drop=False, inplace=True)

            # Calculate indicator 
            # Signal Check 
            filtered_data = veri[veri.stock==stock]
            veri_3 =     filtered_data.groupby(pd.Grouper(key = 'date', freq='5min', offset="1H")).agg({ 'Low': 'min','Close': 'last'}).dropna()
            veri_12 =     filtered_data.groupby(pd.Grouper(key = 'date', freq='15min', offset="1H")).agg({'Low': 'min','Close': 'last'}).dropna()
            t1 = Tillson('tillson',filtered_data,f"stock",t3length=3)
            t2 = Tillson('tillson',filtered_data,f"stock",1.7, t3length=3)
            t3 = Tillson('tillson',veri_3,f"stock",t3length=3)
            t4 = Tillson('tillson',veri_3,f"stock",1.7, t3length=3)
            t5 = Tillson('tillson',veri_12,f"stock",t3length=3)
            t6 = Tillson('tillson',veri_12,f"stock",1.7, t3length=3)
            #print(t1.points[-2:])
            indicators = [t1,t2,t3,t4,t5,t6]
            buy = np.full((len(indicators)),True)
            sell = np.full((len(indicators)),False)
            signal = EqSignal(indicators, buy, sell)
            if len(signal.signs)>0:
                print(signal.signs)
                if signal.islem:
                    print('islem')
                    if signal.side:
                        buy(stock, close)
                        print('buy')
                    else:
                        print('sell')
                        buy(stock, close)
                    print(kasa)
                veri.drop( veri[ veri['date'] < pd.Timestamp(datetime.utcnow()-timedelta(hours=14, minutes=0)) ].index, inplace=True)

            # Buy/Sell

def on_close(ws, close_status_code, close_msg):
    print("closed")
streamList = ""
for s in stockList[0:50]:
  streamList += f"{s.lower()}@kline_1m/"
streamList = streamList[:-1]
SOCK = f"wss://stream.binance.com:9443/stream?streams={streamList}"
ws = websocket.WebSocketApp(SOCK, on_open=on_open,on_close=on_close, on_message=on_message)
#websocket.enableTrace(True)
ws.run_forever()