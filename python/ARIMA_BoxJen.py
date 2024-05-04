import pymongo
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import calendar
import pmdarima as pm
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_squared_error
import warnings
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]


def generate_predictions(stock_data):
    # Create DataFrame from stock_data
    print(f"Processing {stock_data[0]['ticker']}...")
    
    stock_df = pd.DataFrame(stock_data, columns=['index', 'close'])
    stock_df['index'] = pd.to_datetime(stock_df['index'])
    stock_df.set_index('index', inplace=True)
    stock_df.dropna(inplace=True)
    
    train_size = int(len(stock_data) * 4/5)  
    train=stock_df[:train_size]
    train_resampled = train.resample('D').mean()
    train_filled = train_resampled.interpolate(method='linear')
    #print(train_filled)
    test = stock_df.iloc[-(len(stock_data)-train_size+1):]

    model = pm.auto_arima(train_filled['close'], 
                      m=7,                    # frequency of series                      
                      seasonal=True,           # TRUE if seasonal series
                      d=1,                     # let model determine 'd'
                      test='adf',              # use adftest to find optimal 'd'
                      start_p=0, start_q=0,    # minimum p and q
                      max_p=2, max_q=2,        # maximum p and q
                      D=1,                     # let model determine 'D'
                      trace=True,
                      start_P=0,start_Q=0,
                      max_P=2,max_Q=2,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)
    
    p=model.order[0]
    d=model.order[1]
    q=model.order[2]
    P=model.seasonal_order[0]
    D=model.seasonal_order[1]
    Q=model.seasonal_order[2]
    m=model.seasonal_order[3]
    
    model = ARIMA(train_filled['close'], order=(p, d, q), freq='D', seasonal_order=(P, D, Q, m))
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)

    pred = model.fit().forecast(steps=test.shape[0])
    actual_prices=stock_df.close[-len(pred):]
    
    mse = mean_squared_error(actual_prices, pred)

        
    pred_documents = []
    for date, close_pred in zip(test.index, pred):
        pred_doc = {
            'index': date.strftime("%Y-%m-%d"),  # Convert datetime to string
            'close': close_pred,
            'ticker': stock_data[0]['ticker'],
            'MSE':mse
        }
        pred_documents.append(pred_doc)

    return pred_documents


for collection_name in db.list_collection_names():

       
       collection = db[collection_name]
       # Get current date
       current_date = datetime.now()
       start_date = current_date - timedelta(days=700)
       query = {'index': {'$gte': start_date}}
       stock_data = list(collection.find(query))

       if len(stock_data) < 50:
        continue  # Skip to the next collection
       pred_docs=generate_predictions(stock_data)
       pred_collection_name = f"{collection_name}_ARIMA_predicted"
       pred_collection = db[pred_collection_name]
       pred_collection.delete_many({})
       pred_collection.insert_many(pred_docs)

