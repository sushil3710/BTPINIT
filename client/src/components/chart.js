import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

const CandlestickChart = ({ selectedName, selectedInterval }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef(null);
  const [candlestickData, setCandlestickData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        let stockName = selectedName;
        let interval = selectedInterval;
        console.log("C1");

        const response = await fetch(`http://localhost:8080/get-stock/${stockName}?interval=${interval}`);
        const rawData = await response.json();

        // Check if rawData is an array
        if (Array.isArray(rawData)) {
          // Transform raw data into the desired candlestick format
          const transformedData = rawData.map((item) => {
            // Format the date to "yyyy-mm-dd"
            const open = typeof item.open === "number" ? item.open : 0;
            const high = typeof item.high === "number" ? item.high : 0;
            const low = typeof item.low === "number" ? item.low : 0;
            const close = typeof item.close === "number" ? item.close : 0;

            const formattedDate = new Date(item.index).toISOString().split("T")[0];

            return {
              time: formattedDate,
              open,
              high,
              low,
              close,
            };
          });

          setCandlestickData(transformedData);
        } else {
          console.log("C2");
          console.error("Invalid data structure received:", rawData);
        }
      } catch (error) {
        console.log("C3");
        console.error("Error fetching candlestick data:", error);
      }
    };

    fetchData();
  }, [selectedName, selectedInterval]);

  useEffect(() => {
    // Check if candlestickData is not empty before rendering the chart
    if (candlestickData.length === 0) {
      return;
    }

    chartRef.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 700,
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
      console.log("C4");
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
