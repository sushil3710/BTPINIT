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
        print(dfoutput)



def auto_arima(param_max=2,series=pd.Series(),verbose=True):
    # Define the p, d and q parameters to take any value 
    # between 0 and param_max
    p  = q = range(0, param_max+1)
    d=range(0,2)
    print('p=', p)
    print('d=', d)
    print('q=', q)
    # Generate all different combinations of seasonal p, d and q triplets
    pdq = [(x[0], x[1], x[2]) for x in list(itertools.product(p, d, q))]
    
    model_resuls = []
    best_model = {}
    min_aic = 10000000
    
    for param in pdq:
        try:
            mod = sm.tsa.ARIMA(series, order=param)

            results = mod.fit()
            
            if verbose:
                print('ARIMA{}- AIC:{}'.format(param, results.aic))
            model_resuls.append({'aic':results.aic,
                                 'params':param,
                                 'model_obj':results})
            if min_aic>results.aic:
                best_model={'aic':results.aic,
                            'params':param,
                            'model_obj':results}
                min_aic = results.aic
        except Exception as ex:
            print(ex)
    if verbose:
        print("Best Model params:{} AIC:{}".format(best_model['params'],
              best_model['aic']))  
        
    return best_model, model_resuls


def arima_gridsearch_cv(series, cv_splits=2,verbose=True,show_plots=True):
    # prepare train-test split object
    tscv = TimeSeriesSplit(n_splits=cv_splits)
    
    # initialize variables
    splits = []
    best_models = []
    all_models = []
    i = 1
    
    # loop through each CV split
    for train_index, test_index in tscv.split(series):
        print("*"*20)
        print("Iteration {} of {}".format(i,cv_splits))
        i = i + 1
        
        # print train and test indices
        if verbose:
            print("TRAIN:", train_index, "TEST:", test_index)
        splits.append({'train':train_index,'test':test_index})
        
        # split train and test sets
        train_series = series.iloc[train_index]
        test_series = series.iloc[test_index]
        
        print("Train shape:{}, Test shape:{}".format(train_series.shape,
              test_series.shape))
        
        # perform auto arima
        _best_model, _all_models = auto_arima(series=train_series)
        best_models.append(_best_model)
        all_models.append(_all_models)
        
        # display summary for best fitting model
        if verbose:
            print(_best_model['model_obj'].summary())
        results = _best_model['model_obj']
       # plt.figure(figsize=(15, 9))
        # if show_plots:
        #     # show residual plots
        #     residuals = pd.DataFrame(results.resid)
        #     #plt.figure(figsize=(15, 9))
        #     residuals.plot(figsize=(14, 6))
        #     plt.title('Residual Plot')
        #     plt.show()
        #     #plt.figure(figsize=(15, 9))
        #     residuals.plot(kind='kde', figsize=(14, 6))
        #     plt.title('KDE Plot')
        #     plt.show()
        #     print(residuals.describe())
        
        #     # show forecast plot
        #     fig, ax = plt.subplots(figsize=(18, 4))
        #     fig.autofmt_xdate()
        #     ax = train_series.plot(ax=ax)
        #     test_series.plot(ax=ax)
        #     fig = results.plot_predict(test_series.index.min(), 
        #                                test_series.index.max(), 
        #                                dynamic=True,ax=ax,
        #                                plot_insample=False)
        #     plt.title('Forecast Plot ')
        #     plt.legend()
        #     plt.show()
    
    return {'cv_split_index':splits,'all_models':all_models,'best_models':best_models}
    
    




if __name__ == '__main__':
    for collection_name in db.list_collection_names():
       if collection_name != "RELIANCE.NS":
           continue
       
       collection = db[collection_name]

       current_date = datetime.now()
       start_date = current_date - timedelta(days=300)
       query = {'index': {'$gte': start_date}}
       stock_data = list(collection.find(query))
       
       stock_df = pd.DataFrame(stock_data, columns=['index', 'close'])
       stock_df['index'] = pd.to_datetime(stock_df['index'])
       stock_df.set_index('index', inplace=True)
       stock_df.dropna(inplace=True)

       stock_resample = stock_df.resample('D').mean()
       new_df = stock_resample.interpolate(method='linear')
       
       log_series = np.log(new_df.close)
       
       ad_fuller_test(log_series)
       #plot_rolling_stats(log_series)
       
       
       log_series_shift = log_series - log_series.shift()
       log_series_shift = log_series_shift[~np.isnan(log_series_shift)]
       
       ad_fuller_test(log_series_shift)
       #plot_rolling_stats(log_series_shift)
       
       new_df['log_series'] = log_series
       new_df['log_series_shift'] = log_series_shift
       print(new_df)
       # cross validate 
       results_dict = arima_gridsearch_cv(new_df.log_series,cv_splits=5)
