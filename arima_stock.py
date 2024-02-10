import pymongo
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import calendar
import pmdarima as pm
import matplotlib.pyplot as plt
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import statsmodels.api as sm
import numpy as np
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]

from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
import pandas as pd
import warnings
import matplotlib.pyplot as plt


def wmape(y_true, y_pred):
    return np.abs(y_true - y_pred).sum() / np.abs(y_true).sum()

def generate_predictions(stock_data):
    # Create DataFrame from stock_data
    stock_df = pd.DataFrame(stock_data, columns=['index', 'close'])
    stock_df['index'] = pd.to_datetime(stock_df['index'])
    stock_df['unique_id'] = stock_data[0]['ticker']
    stock_df= stock_df.rename(columns={'index': 'ds','close':'y'})
    #stock_df.set_index('index', inplace=True)
    
    # Reindex to include all dates and interpolate missing values
    # all_dates = pd.date_range(start=stock_df.index.min(), end=stock_df.index.max(), freq='D')
    # stock_df = stock_df.reindex(all_dates)
    # stock_df['y'] = stock_df['y'].interpolate(method='nearest')
    print(stock_df)
    
    train = stock_df.loc[stock_df['ds'] < '2024-01-15']
    valid = stock_df.loc[(stock_df['ds'] >= '2024-01-15') & (stock_df['ds'] < '2024-02-09')]
    #h = valid['ds'].nunique()
    
    h = valid.shape[0]
    print(h)
    print(valid)

    # Split data into train and test sets
    #train = stock_df.iloc[:-100]
    #test = stock_df.iloc[-101:]
    # Fit SARIMA model
    model = StatsForecast(models=[AutoARIMA(season_length=7)], freq='D', n_jobs=-1)
    model.fit(train)
    # Predict future values
    pred = model.predict(h=h)
    pred = pred.reset_index().merge(valid, on=['ds','unique_id'], how='left')
    #pred = pred.dropna(subset=['y']) 
    #pred.index = test.index
    wmape_ = wmape(pred['y'].values, pred['AutoARIMA'].values)
    print(f'WMAPE: {wmape_:.2%}')

    # Prepare predicted documents
    pred_documents = []
    for date, close_pred,y in zip(pred['ds'], pred['AutoARIMA'],pred['y']):
        pred_doc = {
            'index': date.strftime("%Y-%m-%d"),  # Convert datetime to string
            'y':y,
            'close': close_pred,
            'ticker': stock_data[0]['ticker']
        }
        pred_documents.append(pred_doc)
    
    pdf = pd.DataFrame(pred_documents)
    print(pdf)    

    return pred_documents


for collection_name in db.list_collection_names():
       if collection_name != "TEJASNET.NS":
        continue
       
       collection = db[collection_name]
    
       # Get current date
       current_date = datetime.now()
    
       start_date = current_date - timedelta(days=300)
       query = {'index': {'$gte': start_date}}
       stock_data = list(collection.find(query))
    
    #    parameters_collection = db["Parameters"]
    #    parameters = parameters_collection.find_one({'ticker': collection_name})
       
    #    if not parameters:
    #        continue
       
    #    p = parameters['p']
    #    d = parameters['d']
    #    q = parameters['q']

       if not (stock_data):
        continue  # Skip to the next collection

       pred_docs=generate_predictions(stock_data)
       pred_collection_name = f"{collection_name}_predicted"
       pred_collection = db[pred_collection_name]
       pred_collection.insert_many(pred_docs)

