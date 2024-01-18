import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import StockChart from "StockChart";


function App() {
    return (
      <BrowserRouter className="font-cereal-font">
        <Routes>
          <Route
            path="/get-stock/:stockName"
            element={
              <PrivateRoute>
                <StockChart />
              </PrivateRoute>
            }
          />
          
        </Routes>
      </BrowserRouter>
    );
}

export default App;




const getData = async (stockName) => {
    try {
        // Make an API call to your server
        const response = await fetch(`http://localhost:8080/api/stock/${stockName}/1Day`);
        
        // Check if the request was successful (status code 200)
        if (!response.ok) {
            throw new Error(`Failed to fetch data: ${response.status} - ${response.statusText}`);
        }

        // Parse the response as JSON
        const data = await response.json();

        // Transform the data into the required format
        const transformedData = data.map((item) => {
            return {
                time: new Date(item.index).getTime() / 1000,
                open: item.open,
                high: item.high,
                low: item.low,
                close: item.close,
            };
        });

        return transformedData;
    } catch (error) {
        console.error(error);
        throw new Error('Failed to fetch data from the server');
    }
};
  
const displayChart = async () => {
    const chartProperties = {
      width: 1500,
      height: 600,
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
    };
  
    //const domElement = document.getElementById('tvchart');
    const chart = LightweightCharts.createChart(domElement, chartProperties);
    const candleseries = chart.addCandlestickSeries();

    try {
        // Fetch data for RELIANCE.NS
        const klinedata = await getData("RELIANCE.NS");
        
        // Set the data in the candlestick series
        candleseries.setData(klinedata);
    } catch (error) {
        console.error(error.message);
        // Handle errors as needed
    }
};

displayChart();
