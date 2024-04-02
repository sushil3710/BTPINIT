from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
from yahoo_fin.stock_info import get_data

class StoreStocks:
    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['stocks']

    # Function to fetch stock data and store in MongoDB
    def fetch_and_store_stocks(self, stock_names):
        today = datetime.today()
        end_d = today.strftime('%m/%d/%Y')

        # Loop through each stock name and fetch historical data
        for stock_name in stock_names:
            try:
                historical_data = get_data(stock_name+".NS", start_date='01/01/2018', end_date=end_d, index_as_date=True, interval='1d')

                if not historical_data.empty:
                    collection_name = stock_name+".NS"  # Use the stock symbol as the collection name
                    historical_data.reset_index(inplace=True)
                    historical_data_dict = historical_data.to_dict(orient='records')
                    self.db[collection_name].insert_many(historical_data_dict)
                    print(f"Data for {stock_name} stored successfully.")
                    
            except Exception as e:
                print(f"Error while fetching or storing data for {stock_name}: {e}")
