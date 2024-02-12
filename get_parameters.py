import pmdarima as pm
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient

# Function to find ARIMA parameters for a single stock
def find_arima_parameters(stock_data):
    print(f"Processing {stock_data[0]['ticker']}...")
    
    stock_df = pd.DataFrame(stock_data, columns=['index', 'close'])
    #stock_df = pd.DataFrame(stock_data)
    stock_df['index'] = pd.to_datetime(stock_df['index'])
    stock_df.set_index('index', inplace=True)
    stock_df.dropna(inplace=True)
    
    # Adjust parameters as needed
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
        'q': model.order[2],
        'P': model.seasonal_order[0],
        'D': model.seasonal_order[1],
        'Q': model.seasonal_order[2],
        'm': model.seasonal_order[3]
    }



if __name__ == '__main__':
    # Connect to MongoDB
    client = MongoClient('localhost', 27017)
    db = client['stocks']
    parameters_collection = db['Parameters']

    # Loop through each collection in the database
    for collection_name in db.list_collection_names():
        # Skip if the collection is not a stock collection
        if collection_name == 'Parameters':
            continue
        
        print(f"Processing collection: {collection_name}")
        
        # Check if parameters already exist for this collection
        if parameters_collection.find_one({'ticker': collection_name}):
            print(f"Parameters already found for collection: {collection_name}. Skipping...")
            continue
        
        # Fetch stock data from MongoDB
        collection = db[collection_name]
        current_date = datetime.now()
        start_date = current_date - timedelta(days=2500)
        end_date = current_date - timedelta(days=300)
        query = {'index': {'$gte': start_date, '$lte': end_date}}
        stock_data = list(collection.find(query))
        
        if len(stock_data) < 10:
            print(f"No data found for collection: {collection_name}. Skipping...")
            continue
        
        # Find ARIMA parameters
        parameters = find_arima_parameters(stock_data)
        print(parameters)
        
        # Insert parameters into the Parameters collection
        parameters_collection.insert_one(parameters)
        
    # Close MongoDB connection
    client.close()
