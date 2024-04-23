import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error


import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]


# Prepare data for LSTM
def create_dataset(dataset, time_steps):
    X, y = [], []
    for i in range(len(dataset) - time_steps):
        X.append(dataset[i:(i + time_steps), :])
        y.append(dataset[i + time_steps, 0])
    return np.array(X), np.array(y)
    
    
# Choose number of time steps for LSTM
def train_model_with_steps(data,step):
    # Choose number of time steps for LSTM
    time_steps = step

    # Create input sequences and labels
    X, y = create_dataset(data, time_steps)

    # Split data into training and validation sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Build LSTM model
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=1))
    
    #adam optimizer with learning rate
    adam = Adam(learning_rate=0.01)

    # Compile model
    model.compile(optimizer=adam, loss='mean_squared_error')

    # Train model
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)

    # Evaluate model
    mse = model.evaluate(X_test, y_test, verbose=0)
    return mse

def generate_predictions(stock_data):
    # Create DataFrame from stock_data
    print(f"Processing {stock_data[0]['ticker']}...")
    
    stock_df = pd.DataFrame(stock_data, columns=['index', 'open','high','low','close','volume'])
    stock_df['index'] = pd.to_datetime(stock_df['index'])
    stock_df.set_index('index', inplace=True)
    stock_df.dropna(inplace=True)

    # Normalize data using Min-Max scaling
    scaler = MinMaxScaler(feature_range=(0, 1))
    
    # Use 'Close' price 
    closing_prices = stock_df['close'].values.reshape(-1, 1)
    final_data = scaler.fit_transform(closing_prices)
    train_data, test_data,_,_= train_test_split(final_data, final_data, test_size=0.2, shuffle=False)
    
    
    # Iterate over different step values and find the best one
    best_step = None
    best_mse = float('inf')
    
    # for step in range(1, 5):  # Try step values from 1 to 20
    #  mse = train_model_with_steps(train_data,step)
    #  print(f"Step: {step}, MSE: {mse}")
    #  if mse < best_mse:
    #     best_mse = mse
    #     best_step = step
    
    # print(f"Best step: {best_step}, Best MSE: {best_mse}")
    # best_step = max(best_step,3)
    # print(f"Best step: {best_step}")

    
    # Train the final model with the best step value
    X_final, y_final = create_dataset(final_data, 1)
    X_train_final, X_test_final, y_train_final, y_test_final = train_test_split(X_final, y_final, test_size=0.2, shuffle=False)
    
    #adam optimizer with learning rate
    adam = Adam(learning_rate=0.1)
    
    final_model = Sequential()
    final_model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train_final.shape[1], X_train_final.shape[2])))
    final_model.add(LSTM(units=50, return_sequences=False))
    final_model.add(Dense(units=1))
    final_model.compile(optimizer=adam, loss='mean_squared_error')
    final_model.fit(X_train_final, y_train_final, epochs=100, batch_size=32, verbose=1)

    # Predictions
    y_pred_scaled = final_model.predict(X_test_final)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    
    
    pred_documents = []

    # Get the dates from the index of the testing set
    test_dates = stock_df.index[-len(y_pred):]
    actual_prices=stock_df.close[-len(y_pred):]
    
    mse = mean_squared_error(actual_prices, y_pred)
    #print("MSE:",mse)
    
    
    for i in range(len(y_pred)):
        pred_doc = {
            'index': test_dates[i].strftime("%Y-%m-%d"),
            'close': float(y_pred[i]),
            'ticker': stock_data[0]['ticker'],
            'MSE':mse
        }
        pred_documents.append(pred_doc)

    return pred_documents


for collection_name in db.list_collection_names():
    # if collection_name != "HDFCBANK.NS":
    #     continue
    #    predicted_collection_name = f"{collection_name}_LSTM_predicted"
   
    #    # Check if this predicted collection name already exists in the database
    #    if predicted_collection_name in db.list_collection_names():
    #        print(f"Collection {predicted_collection_name} already exists.")
    #        continue  # Skip to the next iteration if it exists

       
    collection = db[collection_name]
    # Get current date
    current_date = datetime.now()
    start_date = current_date - timedelta(days=700)
    query = {'index': {'$gte': start_date}}
    stock_data = list(collection.find(query))
    if len(stock_data) < 50:
     continue  # Skip to the next collection
    pred_docs=generate_predictions(stock_data)
    pred_collection_name = f"{collection_name}_LSTM_predicted"
    pred_collection = db[pred_collection_name]
    pred_collection.delete_many({})
    pred_collection.insert_many(pred_docs)