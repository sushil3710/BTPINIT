import React from "react";
import SearchAndChartHeader from "./components/SearchAndChartHeader";
import TimeHeader from "./components/TimeHeader";
import CandlestickChart from "./components/chart";


const App = () => {
  //change this to an api call and fetch data from there
  const candlestickData = [
    {
      time: "2018-10-19",
      open: 180.34,
      high: 180.99,
      low: 178.57,
      close: 179.85,
    },
    {
      time: "2018-10-22",
      open: 180.82,
      high: 181.4,
      low: 177.56,
      close: 178.75,
    },
    {
      time: "2018-10-23",
      open: 175.77,
      high: 179.49,
      low: 175.44,
      close: 178.53,
    },
    {
      time: "2018-10-24",
      open: 178.58,
      high: 182.37,
      low: 176.31,
      close: 176.97,
    },
  ];
  
const selname="RELIANCE.NS";
  return (
    <div className="">
      {/* <h1 className="text-center text-3xl py-2 font-semibold my-2">
        TradingView
      </h1> */}

      {/* <h1 className="mx-8 font-">Candlestick Chart</h1> */}

      {/* <div className="container flex ">
        <input
          class=" mx-4  my-4 p-2 border border-gray-300 rounded-md  flex items-center justify-center"
          placeholder="Enter your stock"
        />
        <button className="bg-blue-700 text-white p-2 my-4 border-r-2 ">
          {" "}
          Search
        </button>
      </div> */}

    {/* <h1 className="flex justify-center text-4xl my-2 text-blue-600 ">CandleStick Chart</h1> */}
      {/* <TimeHeader></TimeHeader> */}
      <SearchAndChartHeader></SearchAndChartHeader>
     {/* <CandlestickChart selectedName={selname} /> */}
    </div>
  );
};

export default App;
