from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
from yahoo_fin.stock_info import get_data
import yfinance as yf

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['stocks']

# Function to fetch stock data and store in MongoDB
def fetch_and_store_stocks(stock_names):
    today = datetime.today()
    end_d = today.strftime('%m/%d/%Y')

    # Loop through each stock name and fetch historical data
    for stock_name in stock_names:
        try:
            historical_data=get_data(stock_name+".NS", start_date = '01/01/2018', end_date=end_d , index_as_date = True, interval = '1d')
            stock = yf.Ticker(stock_name+".NS")
            sector = stock.info['sector']
            
            if not historical_data.empty:

                collection_name = stock_name+".NS"  # Use the stock symbol as the collection name
                historical_data.reset_index(inplace=True)
                # Add sector information to each document
                historical_data['sector'] = sector
                
                historical_data_dict = historical_data.to_dict(orient='records')
                db[collection_name].insert_many(historical_data_dict)

                print(f"Data for {stock_name} stored successfully.")
                
        except Exception as e:
            print(f"Stock not Registered {stock_name}: {e}")

if __name__ == "__main__":
    excel_path = "C:\\Users\\sushi\\Downloads\\BTPINIT\\python\\MCAP31122023.xlsx"
    df = pd.read_excel(excel_path)
    # Read stock names from the Excel file
    stock_names = df['Symbol'].tolist()
    fetch_and_store_stocks(stock_names)