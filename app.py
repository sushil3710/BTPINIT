from flask import Flask, render_template, request
from pymongo import MongoClient
import plotly.express as px
from plotly.offline import plot

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['stocks']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot_stock():
    stock_name = request.form['stock_name']
    duration = request.form['duration']

    # Fetch data from MongoDB
    collection = db[stock_name]
    cursor = collection.find({}, {'_id': 0})
    stock_data = list(cursor)

    # Create Candlestick Chart
    fig = px.candlestick(stock_data, x='date', open='open', high='high', low='low', close='close')

    # Customize chart layout
    fig.update_layout(title=f'{stock_name} Stock Price ({duration})', xaxis_title='Date', yaxis_title='Stock Price')

    # Save the chart as HTML file
    chart_html = plot(fig, output_type='div')

    return render_template('plot.html', chart_html=chart_html)

if __name__ == '__main__':
    app.run(debug=True)
