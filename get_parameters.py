from pymongo import MongoClient
from datetime import datetime, timedelta
from pmdarima.arima import auto_arima
import pandas as pd
import os
import sys 
from multiprocessing import Pool

# Connect to MongoDB
client = MongoClient('localhost', 27017)  # Assuming MongoDB is running on localhost on default port
db = client['stocks']

# Function to find ARIMA parameters for a single stock
def find_arima_parameters(stock_data):
    
    print(f"Processing {stock_data[0]['ticker']}...")
    
    stock_df = pd.DataFrame(stock_data)  # Wrap stock_data in a list
    stock_df['index'] = pd.to_datetime(stock_df['index'])
    stock_df.set_index('index', inplace=True)
    #print(len(stock_df))
    stock_df.dropna(inplace=True)
    
    
    model = auto_arima(stock_df['close'], start_p=1, start_q=1,
                        max_p=3, max_q=3, m=7,
                        start_P=0, seasonal=True,
                        d=None, D=1, trace=True,
                        error_action='ignore',  
                        suppress_warnings=True, 
                        stepwise=True)
    
    
    
    return {
        'ticker': stock_data[0]['ticker'],
        'p': model.order[0],
        'd': model.order[1],
        'q': model.order[2]
    }


if __name__ == '__main__':
    # Fetching stock data from MongoDB
    parameters_collection = db['Parameters']
    stocks_data = []
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        
        current_date = datetime.now()
        start_date = current_date - timedelta(days=1400)
        end_date = current_date - timedelta(days=200)
        query = {'index': {'$gte': start_date, '$lte': end_date}}
        stock_data = list(collection.find(query))
        #print(stock_data)
        if stock_data:  # Check if stock_data is not empty
           parameters = find_arima_parameters(stock_data)
           print(parameters)
           # Inserting parameters into the Parameters collection  
           parameters_collection.insert_one(parameters)
        else:
           print(f"No data found for collection: {collection_name}. Skipping...")
        
        # parameters = find_arima_parameters(stock_data)
        # print(parameters)
        # # Inserting parameters into the Parameters collection  
        # parameters_collection.insert_many(parameters)

    client.close()  # Close MongoDB connection
