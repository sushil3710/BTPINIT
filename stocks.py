
from datetime import datetime, timedelta
import pandas as pd
from nsetools import Nse
from pymongo import MongoClient
from yahoo_fin.stock_info import get_data

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['stocks']

# Function to fetch stock data and store in MongoDB
def fetch_and_store_stocks(stock_names):
   # nse = Nse()

    # Define the time period for historical data (e.g., last 30 days)
    # end_date = datetime.now()
    # print(end_date)
    # start_date = end_date - timedelta(days=30)
    historical_data_dict = {}


    # Loop through each stock name and fetch historical data
    for stock_name in stock_names:
        try:
            historical_data=get_data(stock_name+".NS", start_date = '01/15/2024', end_date='01/17/2024' , index_as_date = True, interval = '1d')
            #historical_data=get_data(stock_name)
            # historical_data = nse.get_historical(stock_name, start_date, end_date)
            
            if not historical_data.empty:

                collection_name = stock_name  # Use the stock symbol as the collection name
                historical_data.reset_index(inplace=True)
                historical_data['index'] = historical_data['index'].apply(lambda date: pd.to_datetime(date).strftime('%Y-%m-%d'))
                historical_data_dict = historical_data.to_dict(orient='records')
                #historical_data['index'] = historical_data['index'].apply(lambda date: pd.to_datetime(date).strftime('%Y-%m-%d'))
                # Insert data into MongoDB
                db[collection_name].insert_many(historical_data_dict)

                print(f"Data for {stock_name} stored successfully.")
        except Exception as e:
            print(f"Error fetching data for {stock_name}: {e}")

if __name__ == "__main__":
    excel_path = 'MCAP31122023.xlsx'
    # Read stock names from the Excel file
    df = pd.read_excel(excel_path)
    stock_names = df['Symbol'].tolist()
    fetch_and_store_stocks(stock_names)