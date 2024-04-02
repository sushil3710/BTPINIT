import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense

import numpy as np

class LSTMmodel:
    def __init__(self):
        pass

    # Prepare data for LSTM
    def create_dataset(self, dataset, time_steps):
        X, y = [], []
        for i in range(len(dataset) - time_steps):
            X.append(dataset[i:(i + time_steps), :])
            y.append(dataset[i + time_steps, 0])
        return np.array(X), np.array(y)

    # Choose number of time steps for LSTM
    def train_model_with_steps(self, data, step):
        # Choose number of time steps for LSTM
        time_steps = step

        # Create input sequences and labels
        X, y = self.create_dataset(data, time_steps)

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # Build LSTM model
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dense(units=1))

        # Compile model
        model.compile(optimizer='adam', loss='mean_squared_error')

        # Train model
        model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)

        # Evaluate model
        mse = model.evaluate(X_test, y_test, verbose=0)
        return mse

    def generate_predictions(self, stock_data):
     
        print(f"Processing {stock_data[0]['ticker']} By LSTM...")
        
        stock_df = pd.DataFrame(stock_data, columns=['index', 'close'])
        stock_df['index'] = pd.to_datetime(stock_df['index'])
        stock_df.set_index('index', inplace=True)
        stock_df.dropna(inplace=True)
    
        # Normalize data using Min-Max scaling
        scaler = MinMaxScaler(feature_range=(0, 1))
        
        # Use 'Close' price 
        closing_prices = stock_df['close'].values.reshape(-1, 1)
        final_data = scaler.fit_transform(closing_prices)
        
        # train_scaled = scaler.fit_transform(train_filled)
        # test_scaled = scaler.transform(test)
        
        # Iterate over different step values and find the best one
        best_step = None
        best_mse = float('inf')
        
        for step in range(1, 5):  # Try step values from 1 to 20
         mse = self.train_model_with_steps(final_data,step)
         print(f"Step: {step}, MSE: {mse}")
         if mse < best_mse:
            best_mse = mse
            best_step = step
        
        print(f"Best step: {best_step}, Best MSE: {best_mse}")
        best_step = max(best_step,3)
        print(f"Best step: {best_step}")
    
        
        # Train the final model with the best step value
        X_final, y_final = self.create_dataset(final_data, best_step)
        X_train_final, X_test_final, y_train_final, y_test_final = train_test_split(X_final, y_final, test_size=0.2, shuffle=False)
        
        final_model = Sequential()
        final_model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train_final.shape[1], X_train_final.shape[2])))
        final_model.add(LSTM(units=50, return_sequences=False))
        final_model.add(Dense(units=1))
        final_model.compile(optimizer='adam', loss='mean_squared_error')
        final_model.fit(X_train_final, y_train_final, epochs=10, batch_size=32, verbose=1)
    
        # Predictions
        y_pred_scaled = final_model.predict(X_test_final)
        y_pred = scaler.inverse_transform(y_pred_scaled)
        
        pred_documents = []
        # Get the dates from the index of the testing set
        test_dates = stock_df.index[-len(y_pred):]
        
        for i in range(len(y_pred)):
            pred_doc = {
                'index': test_dates[i].strftime("%Y-%m-%d"),
                'close': float(y_pred[i]),
                'ticker': stock_data[0]['ticker']
            }
            pred_documents.append(pred_doc)
    
        return pred_documents

