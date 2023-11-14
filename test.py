from datetime import datetime,timedelta
import pandas as pd
veri = pd.DataFrame(columns =['stock', 'date', 'Close', 'Low'])
veri.set_index('stock')
dates = []
for i in range(100):
  dates.append(pd.Timestamp(datetime.utcnow()-timedelta(minutes=i*5)))
veri['date'] = dates


