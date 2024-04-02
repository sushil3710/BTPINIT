from StoreStocks import StoreStocks
from python.ClassBased.LSTMmodel import LSTM_predictor
import pymongo
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]

def StoringData(): 
    # Instantiate the StoreStocks class
    
    handler = StoreStocks()
    excel_path = 'MCAP31122023.xlsx'
    df = pd.read_excel(excel_path)
    stock_names = df['Symbol'].tolist()

    # Call the fetch_and_store_stocks method
    handler.fetch_and_store_stocks(stock_names)

def LSTM_(): 
    # Instantiate the StoreStocks class
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["stocks"]
    predictor = LSTM_predictor()
    for collection_name in db.list_collection_names():
        if collection_name != "BAJAJELEC.NS":
            continue
    
        collection = db[collection_name]
        # Get current date
        current_date = datetime.now()
        start_date = current_date - timedelta(days=400)
        query = {'index': {'$gte': start_date}}
        stock_data = list(collection.find(query))
    
        if len(stock_data) < 50:
            continue  # Skip to the next collection
        pred_docs = predictor.generate_predictions(stock_data)
        pred_collection_name = f"{collection_name}_LSTM_predicted"
        pred_collection = db[pred_collection_name]
        pred_collection.delete_many({})
        pred_collection.insert_many(pred_docs)


if __name__=="__main__": 
    #StoringData()
    LSTM_()
    

         