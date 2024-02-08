import pymongo
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import calendar
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]



# Define function to generate predictions for a stock
def generate_predictions_daily(stock_data):
    # Extract relevant data
    daily_opens = [day['open'] for day in stock_data]
    daily_highs = [day['high'] for day in stock_data]
    daily_lows = [day['low'] for day in stock_data]
    daily_closes = [day['close'] for day in stock_data]
    daily_adjcloses = [day['adjclose'] for day in stock_data]

    end_date = stock_data[-1]['index']
 
    # Fit ARIMA models for each value
    open_model = ARIMA(daily_opens, order=(0, 1, 0))
    high_model = ARIMA(daily_highs, order=(0, 1, 0))
    low_model = ARIMA(daily_lows, order=(0, 1, 0))
    close_model = ARIMA(daily_closes, order=(0, 1, 0))
    adjclose_model = ARIMA(daily_adjcloses, order=(0, 1, 0))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)

    open_prediction = open_model.fit().forecast(steps=1)[0]
    high_prediction = high_model.fit().forecast(steps=1)[0]
    low_prediction = low_model.fit().forecast(steps=1)[0]
    close_prediction = close_model.fit().forecast(steps=1)[0]
    adjclose_prediction = adjclose_model.fit().forecast(steps=1)[0]
    
    pred_document = {
        'index': end_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        'open': open_prediction,
        'high': high_prediction,
        'low': low_prediction,
        'close': close_prediction,
        'adjclose': adjclose_prediction,
        'ticker': stock_data[0]['ticker']
    }

    
    return pred_document




# Define function to generate predictions for a stock
def generate_predictions_monthly(stock_data):
    # Extract relevant data

    #print(stock_data)
    monthly_dates = []
    monthly_opens = []
    monthly_highs = []
    monthly_lows = []
    monthly_closes = []
    monthly_adjcloses = []

    current_date = stock_data[0]['index']
    end_date = stock_data[-1]['index']
 
    while current_date <= end_date:
        # Find the closest available date on or after the 30th day from the current date
        target_date = current_date + timedelta(days=30)
        closest_date = min(stock_data, key=lambda x: abs(x['index'] - target_date))

        # Append values to the monthly lists
        monthly_opens.append(closest_date['open'])
        monthly_highs.append(closest_date['high'])
        monthly_lows.append(closest_date['low'])
        monthly_closes.append(closest_date['close'])
        monthly_adjcloses.append(closest_date['adjclose'])

        # Update the current date to the next available date
        current_date = closest_date['index'] + timedelta(days=1)

    
    # Fit ARIMA models for each value
    open_model = ARIMA(monthly_opens, order=(0,1,0))
    high_model = ARIMA(monthly_highs, order=(0,1,0))
    low_model = ARIMA(monthly_lows, order=(0,1,0))
    close_model = ARIMA(monthly_closes, order=(0,1,0))
    adjclose_model = ARIMA(monthly_adjcloses, order=(0,1,0))

    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)

   

    open_prediction = open_model.fit().forecast(steps=1)[0]
    high_prediction = high_model.fit().forecast(steps=1)[0]
    low_prediction = low_model.fit().forecast(steps=1)[0]
    close_prediction = close_model.fit().forecast(steps=1)[0]
    adjclose_prediction = adjclose_model.fit().forecast(steps=1)[0]
    
    pred_document = {
        'index': end_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        'open': open_prediction,
        'high': high_prediction,
        'low': low_prediction,
        'close': close_prediction,
        'adjclose': adjclose_prediction,
        'ticker': stock_data[0]['ticker']
    }

    
    return pred_document




def generate_predictions_weekly(stock_data):
    # Extract relevant data

    #print(stock_data)
    weekly_dates = []
    weekly_opens = []
    weekly_highs = []
    weekly_lows = []
    weekly_closes = []
    weekly_adjcloses = []

    current_date = stock_data[0]['index']
    end_date = stock_data[-1]['index']
 
    while current_date <= end_date:
        # Find the closest available date on or after the 30th day from the current date
        target_date = current_date + timedelta(days=7)
        closest_date = min(stock_data, key=lambda x: abs(x['index'] - target_date))

        # Append values to the monthly lists
        weekly_opens.append(closest_date['open'])
        weekly_highs.append(closest_date['high'])
        weekly_lows.append(closest_date['low'])
        weekly_closes.append(closest_date['close'])
        weekly_adjcloses.append(closest_date['adjclose'])

        # Update the current date to the next available date
        current_date = closest_date['index'] + timedelta(days=1)

    
    # Fit ARIMA models for each value
    open_model = ARIMA(weekly_opens, order=(0,1,0))
    high_model = ARIMA(weekly_highs, order=(0,1,0))
    low_model = ARIMA(weekly_lows, order=(0,1,0))
    close_model = ARIMA(weekly_closes, order=(0,1,0))
    adjclose_model = ARIMA(weekly_adjcloses, order=(0,1,0))

    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)

    

    open_prediction = open_model.fit().forecast(steps=1)[0]
    high_prediction = high_model.fit().forecast(steps=1)[0]
    low_prediction = low_model.fit().forecast(steps=1)[0]
    close_prediction = close_model.fit().forecast(steps=1)[0]
    adjclose_prediction = adjclose_model.fit().forecast(steps=1)[0]
    
    pred_document = {
        'index': end_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        'open': open_prediction,
        'high': high_prediction,
        'low': low_prediction,
        'close': close_prediction,
        'adjclose': adjclose_prediction,
        'ticker': stock_data[0]['ticker']
    }

    
    return pred_document

def generate_predictions_yearly(stock_data):
    # Extract relevant data

    #print(stock_data)
    yearly_dates = []
    yearly_opens = []
    yearly_highs = []
    yearly_lows = []
    yearly_closes = []
    yearly_adjcloses = []

    current_date = stock_data[0]['index']
    end_date = stock_data[-1]['index']
 
    while current_date <= end_date:
        # Find the closest available date on or after the 30th day from the current date
        target_date = current_date + timedelta(days=365)
        closest_date = min(stock_data, key=lambda x: abs(x['index'] - target_date))

        # Append values to the monthly lists
        yearly_opens.append(closest_date['open'])
        yearly_highs.append(closest_date['high'])
        yearly_lows.append(closest_date['low'])
        yearly_closes.append(closest_date['close'])
        yearly_adjcloses.append(closest_date['adjclose'])

        # Update the current date to the next available date
        current_date = closest_date['index'] + timedelta(days=1)

    
    # Fit ARIMA models for each value
    open_model = ARIMA(yearly_opens, order=(0,1,0))
    high_model = ARIMA(yearly_highs, order=(0,1,0))
    low_model = ARIMA(yearly_lows, order=(0,1,0))
    close_model = ARIMA(yearly_closes, order=(0,1,0))
    adjclose_model = ARIMA(yearly_adjcloses, order=(0,1,0))

    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)

    

    open_prediction = open_model.fit().forecast(steps=1)[0]
    high_prediction = high_model.fit().forecast(steps=1)[0]
    low_prediction = low_model.fit().forecast(steps=1)[0]
    close_prediction = close_model.fit().forecast(steps=1)[0]
    adjclose_prediction = adjclose_model.fit().forecast(steps=1)[0]
    
    pred_document = {
        'index': end_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        'open': open_prediction,
        'high': high_prediction,
        'low': low_prediction,
        'close': close_prediction,
        'adjclose': adjclose_prediction,
        'ticker': stock_data[0]['ticker']
    }

    
    return pred_document


# Iterate through stocks collections

for collection_name in db.list_collection_names():
    collection = db[collection_name]
    
    # Get current date
    current_date = datetime.now()

    #Daily
    start_date = current_date - timedelta(days=12)
    end_date = current_date - timedelta(days=2)
    query = {'index': {'$gte': start_date, '$lte': end_date}}
    stock_data = list(collection.find(query))
    if not stock_data:
     print(f"No data found in collection '{collection_name}' for the specified date range.")
     continue  # Skip to the next collection
    pred_documents = generate_predictions_daily(stock_data)
    pred_collection_name = f"{collection_name}_1day"
    pred_collection = db[pred_collection_name]
    pred_collection.insert_one(pred_documents)
    

    #Weekly
    start_date = current_date - timedelta(days=49)
    end_date = current_date - timedelta(days=8)
    query = {'index': {'$gte': start_date, '$lte': end_date}}
    stock_data = list(collection.find(query))
    if not stock_data:
     print(f"No data found in collection '{collection_name}' for the specified date range.")
     continue  # Skip to the next collection
    pred_documents = generate_predictions_monthly(stock_data)
    pred_collection_name = f"{collection_name}_1week"
    pred_collection = db[pred_collection_name]
    pred_collection.insert_one(pred_documents)
    
    
    #Monthly
    start_date = current_date - timedelta(days=300)
    end_date = current_date - timedelta(days=30)
    query = {'index': {'$gte': start_date, '$lte': end_date}}
    stock_data = list(collection.find(query))
    if not stock_data:
     print(f"No data found in collection '{collection_name}' for the specified date range.")
     continue  # Skip to the next collection
    pred_documents = generate_predictions_monthly(stock_data)
    pred_collection_name = f"{collection_name}_1month"
    pred_collection = db[pred_collection_name]
    pred_collection.insert_one(pred_documents)


    #Yearly
    start_date = current_date - timedelta(days=2200)
    end_date = current_date - timedelta(days=365)
    query = {'index': {'$gte': start_date, '$lte': end_date}}
    stock_data = list(collection.find(query))
    if not stock_data:
     print(f"No data found in collection '{collection_name}' for the specified date range.")
     continue  # Skip to the next collection
    pred_documents = generate_predictions_monthly(stock_data)
    pred_collection_name = f"{collection_name}_1year"
    pred_collection = db[pred_collection_name]
    pred_collection.insert_one(pred_documents)
