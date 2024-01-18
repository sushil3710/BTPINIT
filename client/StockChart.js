import React, { useState, useEffect } from 'react';
import { createChart, CandlestickSeries } from 'lightweight-charts';

const StockChart = () => {
  const [stockData, setStockData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/get-stock/RELIANCE.NS'); // Replace with your API endpoint
        const data = await response.json();
        setStockData(data);
      } catch (error) {
        console.error('Error fetching stock data:', error);
      }
    };

    fetchData();
  }, []);

  // useEffect(() => {
  //   if (stockData.length > 0) {
  //     renderChart();
  //   }
  // }, [stockData]);

   // const renderChart = () => {
    const chart = createChart('stock-chart', { width: 800, height: 400 });
    const candlestickSeries = chart.addCandlestickSeries();

    const chartData = stockData.map(({ index, open, close, high, low }) => ({
      time: new Date(index).getTime() / 1000, // Make sure to convert time to seconds
      open: parseFloat(open),
      close: parseFloat(close),
      high: parseFloat(high),
      low: parseFloat(low),
    }));

    candlestickSeries.setData(chartData);
 // };

  return (
    <div>
      <h1>Stock Candlestick Chart</h1>
      <div id="stock-chart"></div>
    </div>
  );
};

export default StockChart;


