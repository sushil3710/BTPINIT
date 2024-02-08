import pymongo
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import calendar
import pandas as pd
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]

def generate_predictions(stock_data, p, q, d,dates_data):
    # Extract close values from the list of dictionaries
    close_values = [entry['close'] for entry in stock_data]
    dates=[entry['index'] for entry in dates_data]
    
    # Fit ARIMA model for close values
    close_model = ARIMA(close_values, order=(p, d, q))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        close_model_fit = close_model.fit()
    
    # Generate predictions for the next 30 days
    start_date =stock_data[-1]['index']
    end_date = start_date + timedelta(days=30)
    predicted_dates = pd.date_range(start=start_date, end=end_date)
    predicted_dates = [date for date in predicted_dates if date in dates]
    close_predictions = close_model_fit.forecast(steps=len(predicted_dates))

    # Prepare the predicted documents
    predicted_documents = []
    for date, close_prediction in zip(predicted_dates, close_predictions):
        pred_document = {
            'index': date.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            'close': close_prediction,
            'ticker': stock_data[0]['ticker']
        }
        predicted_documents.append(pred_document)

    pdf=pd.DataFrame(predicted_documents)
    print(pdf)    

    return predicted_documents

for collection_name in db.list_collection_names():
       collection = db[collection_name]
    
       # Get current date
       current_date = datetime.now()
    
       start_date = current_date - timedelta(days=600)
       end_date = current_date - timedelta(days=200)
       query = {'index': {'$gte': start_date, '$lte': end_date}}
       query_dates = {'index': {'$gte': end_date}}
       dates_data=list(collection.find(query_dates))
       stock_data = list(collection.find(query))
    
       parameters_collection = db["Parameters"]
       parameters = parameters_collection.find_one({'ticker': collection_name})
       p = parameters['p']
       q = parameters['q']
       d = parameters['d']

       if not stock_data:
        continue  # Skip to the next collection

       pred_documents = generate_predictions(stock_data,p,q,d,dates_data)
       pred_collection_name = f"{collection_name}_predicted"
       pred_collection = db[pred_collection_name]
       pred_collection.insert_many(pred_documents)

