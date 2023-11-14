
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import talib
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
class PiriReis:
  def __init__(self, hisse, interval,raw_data):
    self.hisse = hisse
    self.interval = interval
    self.raw_data = raw_data
    self.raw_data['date'] = pd.to_datetime(self.raw_data['date'], unit='ms')

    self.load_data()
    self.price = self.data["Close"]

  def change_interval(self, interval='5min'):
    return self.raw_data.groupby(pd.Grouper(key = 'date', freq=interval,offset='1hour')).agg({'Open': 'first',
                                                          'High': 'max',
                                                          'Low': 'min',
                                                          'Close': 'last'}).dropna()
    self.data.dropna(inplace=True)
  def load_data(self):
    self.raw_data.set_index('date')
    self.data = self.raw_data.groupby(pd.Grouper(key = 'date', freq=self.interval, offset='1hour')).agg({'Open': 'first',
                                                          'High': 'max',
                                                          'Low': 'min',
                                                          'Close': 'last'}).dropna()
from plotly.subplots import make_subplots

class Tillson:
  @staticmethod
  def calculate(data, vf, t3):
      ema_first_input = (data.Close + data.Low + 2 * data.Close) / 4
      e1 = talib.EMA(ema_first_input, t3)
      e2 = talib.EMA(e1, t3)
      e3 = talib.EMA(e2, t3)
      e4 = talib.EMA(e3, t3)
      e5 = talib.EMA(e4, t3)
      e6 = talib.EMA(e5, t3)
      c1 = -1 * vf**3
      c2 = 3 * vf**2 + 3 * vf**3
      c3 = -6 * vf **2 - 3 * vf - 3 * vf**3
      c4 = 1 + 3 * vf + vf**3 + 3 * vf**2
      T3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
      return T3

class EqSignal:
      @staticmethod
      def calculate(indicators):
        i=0
        signs = [np.sign(np.diff(ind)) for ind in indicators]
        while i<len(signs)-2:
            if signs[i] == signs[i+1]:
                i+=1
            else:
                break
        if i==len(signs)-2:
           return (True, signs[0][0] == 1)
        else:
           return (False, -1)
        
        
