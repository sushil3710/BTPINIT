// import React, { useEffect, useRef } from "react";
// import { createChart } from "lightweight-charts";

// const CandlestickChart = ({ data }) => {
//   const chartContainerRef = useRef();

//   useEffect(() => {
//     const chart = createChart(chartContainerRef.current, {
//       width: chartContainerRef.current.clientWidth,
//       height: 480,

	   
//     });

//     const candlestickSeries = chart.addCandlestickSeries({
//       upColor: "rgba(0, 150, 36, 1)",
//       downColor: "rgba(255, 0, 0, 1)",
//       borderUpColor: "rgba(0, 150, 36, 1)",
//       borderDownColor: "rgba(255, 0, 0, 1)",
//       wickUpColor: "rgba(0, 150, 36, 1)",
//       wickDownColor: "rgba(255, 0, 0, 1)",
//     });

//     candlestickSeries.setData(data);

//     const handleResize = () => {
//       chart.applyOptions({ width: chartContainerRef.current.clientWidth });
//     };

//     window.addEventListener("resize", handleResize);

//     return () => {
//       window.removeEventListener("resize", handleResize);
//       chart.remove();
//     };
//   }, [data]);

//   return <div ref={chartContainerRef} />;
// };

// export default CandlestickChart;


import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

const CandlestickChart = ({ selectedName }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef(null);
  const [candlestickData, setCandlestickData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/get-stock/${selectedName}`);
        const rawData = await response.json();

        // Transform raw data into the desired candlestick format
        const transformedData = rawData.data.map(item => ({
          time: item.index,  // Assuming 'index' is the time attribute
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }));

        setCandlestickData(transformedData);
      } catch (error) {
        console.error("Error fetching candlestick data:", error);
      }
    };

    fetchData();
  }, [selectedName]);

  useEffect(() => {
    chartRef.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 480,
    });

    const candlestickSeries = chartRef.current.addCandlestickSeries({
      upColor: "rgba(0, 150, 36, 1)",
      downColor: "rgba(255, 0, 0, 1)",
      borderUpColor: "rgba(0, 150, 36, 1)",
      borderDownColor: "rgba(255, 0, 0, 1)",
      wickUpColor: "rgba(0, 150, 36, 1)",
      wickDownColor: "rgba(255, 0, 0, 1)",
    });

    candlestickSeries.setData(candlestickData);

    const handleResize = () => {
      chartRef.current.applyOptions({
        width: chartContainerRef.current.clientWidth,
      });
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chartRef.current.remove();
    };
  }, [candlestickData]);

  return <div ref={chartContainerRef} />;
};

export default CandlestickChart;
