import pymongo
import itertools
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.model_selection import TimeSeriesSplit
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
from matplotlib.pyplot import figure
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tools.sm_exceptions import ConvergenceWarning



sns.set_style('whitegrid')
sns.set_context('talk')

import warnings

def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]

def plot_rolling_stats(ts):
        figure(num=None, figsize=(18, 7), dpi=80, linewidth=5)
        rolling_mean = ts.rolling(window=24,center=False).mean()
        rolling_std = ts.rolling(window=24,center=False).std()

        #Plot rolling statistics:
        orig = plt.plot(ts, color='c',label='Original')
        mean = plt.plot(rolling_mean, color='red', label='Rolling Mean')
        std = plt.plot(rolling_std, color='black', label = 'Rolling Std')
        
        plt.legend(loc='best')
        plt.title('Rolling Mean & Standard Deviation')
        plt.show(block=False)



def ad_fuller_test(ts):
    dftest = adfuller(ts, autolag='AIC')
      
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
        #print(dfoutput)



def generate_predictions(train_filled,test,ticker,params):
    
    p=params['order'][0]
    d=params['order'][1]
    q=params['order'][2]
    P=params['seasonal_order'][0]
    D=params['seasonal_order'][1]
    Q=params['seasonal_order'][2]
    m=params['seasonal_order'][3]
    
    
    model = ARIMA(train_filled['close'], order=(p, d, q), freq='D', seasonal_order=(P, D, Q, m))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)

    pred = model.fit().forecast(steps=test.shape[0])
    pred_documents = []
    for date, close_pred in zip(test.index, pred):
        pred_doc = {
            'index': date.strftime("%Y-%m-%d"),  # Convert datetime to string
            'close': close_pred,
            'ticker': ticker
        }
        pred_documents.append(pred_doc)
    return pred_documents    

def auto_arima(param_max=1, series=pd.Series(), seasonal_param_max=1, m=7, verbose=True):
    # Define the p, d, and q parameters to take any value between 0 and param_max
    p = q = range(0, param_max+1)
    d = 1
    
    # Define the seasonal P, D, and Q parameters to take any value between 0 and seasonal_param_max
    P  = range(0, seasonal_param_max+1)
    Q  = range(0, seasonal_param_max+1)
    D = 1
    
    #Combinations:  d=0 D=1 m=7(Not good, Multi curve Repeations in a line),  d=1 D=1 m=7(Not good, simple increasing line), d=0 D=1 m=30(Not good Results,Time Exceeds), d=1 D=1 m=30(Time Limit Exceeds), d=1 D=0 m=30(no peaks and changes as no Seasonal Differencing) 
    #d=1 D=1 m=30 p,q,P,Q=range(1,3)  (Graph better but not as expected),
    #
    #cominations:(Keep Non seasonale Parameters constant 0,1,2): 
    #cominations:(Only non Sea): 
    
    
    # print('p=', p)
    # print('d=', d)
    # print('q=', q)
    # print('P=', P)
    # print('D=', D)
    # print('Q=', Q)
    # print('m=', m)
    
    # Generate all different combinations of p, d, and q triplets
    pdq = [(x[0], d, x[1]) for x in list(itertools.product(p, q))]
    seasonal_pdq = [(x[0], D, x[1], m) for x in list(itertools.product(P, Q))]
    
    model_results = []
    best_model = {}
    min_aic = float('inf')
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        for param in pdq:
          for param_seasonal in seasonal_pdq:
            try:
                mod = sm.tsa.ARIMA(series, order=param, freq='D',seasonal_order=param_seasonal)
                results = mod.fit()

                
                
                if verbose:
                    print('ARIMA{}{} - AIC:{}'.format(param, param_seasonal, results.aic))
                    model_results.append({'aic': results.aic,
                                      'params': {'order': param, 'seasonal_order': param_seasonal},
                                      'model_obj': results})

                
                if results.aic < min_aic:
                    best_model = {'aic': results.aic,
                                  'params': {'order': param, 'seasonal_order': param_seasonal},
                                  'model_obj': results}
                    min_aic = results.aic
            except Exception as ex:
                print(ex)
                import traceback
                traceback.print_exc()
                
    if verbose:
        print("Best Model params:{} AIC:{}".format(best_model['params'], best_model['aic']))  
    
    return best_model, model_results 
    

if __name__ == '__main__':
    for collection_name in db.list_collection_names():
       if collection_name != "BAJAJELEC.NS":
           continue
       
       collection = db[collection_name]
       current_date = datetime.now()
       start_date = current_date - timedelta(days=400)
       query = {'index': {'$gte': start_date}}
       stock_data = list(collection.find(query))
       
       if len(stock_data) < 50:
        continue  # Skip to the next collection
       
       stock_df = pd.DataFrame(stock_data, columns=['index', 'close'])
       stock_df['index'] = pd.to_datetime(stock_df['index'])
       stock_df.set_index('index', inplace=True)
       stock_df.dropna(inplace=True)
       
       train_size = int(len(stock_data) * 4/5)  
       train=stock_df[:train_size]
       train_resampled = train.resample('D').mean()
       train_filled = train_resampled.interpolate(method='linear')
       test = stock_df.iloc[-(len(stock_data)-train_size+1):]

       new_df = train_filled
       log_series = np.log(new_df.close)
       #ad_fuller_test(log_series)
       #plot_rolling_stats(log_series)
    
       log_series_shift = log_series - log_series.shift()
       log_series_shift = log_series_shift[~np.isnan(log_series_shift)]
       
       #ad_fuller_test(log_series_shift)
       #plot_rolling_stats(log_series_shift)
       
       new_df['log_series'] = log_series
       new_df['log_series_shift'] = log_series_shift
       #print(new_df)
       # cross validate 
       
       #Here log series is passed to get the parameters
       print(f"Processing {stock_data[0]['ticker']}...")
       best_model, all_models = auto_arima(series=new_df.log_series)
       #best_model, all_models = auto_arima(series=new_df.close)
       
       params = best_model['params']
       pred_docs=generate_predictions(train_filled,test,stock_data[0]['ticker'],params)
       
       pred_collection_name = f"{collection_name}_predicted_BoxJen"
       pred_collection = db[pred_collection_name]
       pred_collection.delete_many({})
       pred_collection.insert_many(pred_docs)
       
       
