import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stocks"]

# Define the GCN model
class GCN(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(GCN, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x, adj):
        x = F.relu(self.fc1(x))
        x = torch.mm(adj, x)
        x = self.fc2(x)
        return x

def train_model(model, adj, features, labels, epochs=100, lr=0.1):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(features, adj)
        loss = criterion(output, labels)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item()}')

def predict(model, adj, features):
    model.eval()
    with torch.no_grad():
        output = model(features, adj)
    return output

def generate_predictions(stock_data):
    print(f"Processing {stock_data[0]['ticker']}...")
    stock_df = pd.DataFrame(stock_data, columns=['index', 'open', 'high', 'low', 'close', 'volume'])
    stock_df['index'] = pd.to_datetime(stock_df['index'])
    stock_df.set_index('index', inplace=True)
    stock_df.dropna(inplace=True)

    scaler = MinMaxScaler(feature_range=(0, 1))
    closing_prices = stock_df['close'].values.reshape(-1, 1)
    final_data = scaler.fit_transform(closing_prices)
    features = stock_df['open'].values.reshape(-1, 1)
    labels = stock_df['close'].values.reshape(-1, 1)
    features = scaler.fit_transform(features)
    labels = scaler.fit_transform(labels)

    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, shuffle=False)
    adjacency_matrix_train = np.eye(len(X_train))
    adjacency_matrix_test = np.eye(len(X_test))
    

    features_train = torch.FloatTensor(X_train)
    features_test = torch.FloatTensor(X_test)
    labels_train=torch.FloatTensor(y_train)
    labels_test=torch.FloatTensor(y_test)
    adj_tensor_train = torch.FloatTensor(adjacency_matrix_train)
    adj_tensor_test = torch.FloatTensor(adjacency_matrix_test)

    model = GCN(input_dim=1, hidden_dim=64, output_dim=1)
    train_model(model, adj_tensor_train, features_train, labels_train)#features =labels as we used only closed price

    predicted_normalized = predict(model, adj_tensor_test, features_test)
    predicted_test = scaler.inverse_transform(predicted_normalized.numpy())

    test_dates = stock_df.index[-len(predicted_test):]
    actual_prices = stock_df['close'][-len(predicted_test):]
    
    #print("pred Pricees:",predicted_test)
    
    mse = mean_squared_error(actual_prices, predicted_test)
    print("MSE:", mse)

    pred_documents = [{'index': date.strftime("%Y-%m-%d"), 'close': float(pred), 'ticker': stock_data[0]['ticker'], 'MSE': mse}
                      for date, pred in zip(test_dates, predicted_test)]

    return pred_documents

for collection_name in db.list_collection_names():
    #print(collection_name)
    # if collection_name != "HDFCBANK.NS":
    #     continue
    
    # predicted_collection_name = f"{collection_name}_GCN_predicted"
    
    # # Check if this predicted collection name already exists in the database
    
    # if predicted_collection_name in db.list_collection_names():
    #     print(f"Collection {predicted_collection_name} already exists.")
    #     continue  # Skip to the next iteration if it exists
    
    collection = db[collection_name]
    current_date = datetime.now()
    start_date = current_date - timedelta(days=700)
    stock_data = list(collection.find({'index': {'$gte': start_date}}))
    if len(stock_data) < 50:
        continue

    pred_docs = generate_predictions(stock_data)
    pred_collection_name = f"{collection_name}_GCN_predicted"
    pred_collection = db[pred_collection_name]
    pred_collection.delete_many({})
    pred_collection.insert_many(pred_docs)
