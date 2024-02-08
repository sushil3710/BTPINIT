import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

const CandlestickChart = ({ selectedName, selectedInterval }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef(null);
  const [candlestickData, setCandlestickData] = useState([]);
  const [lineData, setLineData] = useState([]);
  const [timeValues, setTimeValues] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        let stockName = selectedName;
        let interval = selectedInterval;

        const response = await fetch(`http://localhost:8080/get-stock/${stockName}/${interval}`);
        const rawData = await response.json();
        const lineResponse = await fetch(`http://localhost:8080/get-prediction/${stockName}`);
        const lineRawData = await lineResponse.json();
      
        if (Array.isArray(rawData)) {
          const transformedData = rawData.map((item) => ({
            time: new Date(item.index).toISOString().split("T")[0],
            open: typeof item.open === "number" ? item.open : 0,
            high: typeof item.high === "number" ? item.high : 0,
            low: typeof item.low === "number" ? item.low : 0,
            close: typeof item.close === "number" ? item.close : 0
          }));
          setCandlestickData(transformedData);
          
          // const times = rawData.map((item) => new Date(item.index).toISOString().split("T")[0]);
          // setTimeValues(times);

          if (Array.isArray(lineRawData)) {
            const transformedData = lineRawData.map((item) => ({
              time: new Date(item.index).toISOString().split("T")[0],
              close: typeof item.close === "number" ? item.close : 0
            }));
            setLineData(transformedData);
          
        } else {
          console.error("Invalid candlestick data structure received:", rawData);
        }

    }
  }
      catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [selectedName, selectedInterval]);

  useEffect(() => {
    if (candlestickData.length === 0 || lineData.length === 0) {
      return;
    }

    chartRef.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: window.innerHeight - 100,
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



    const lineSeries = chartRef.current.addLineSeries({ color: 'blue', lineWidth: 3 });
    lineSeries.setData(lineData);

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
  }, [candlestickData, lineData]);

  return (
    <div>
      <div className="stock-name"  style={{ fontWeight: 'bold', marginLeft: '10px' }}>{selectedName}</div>
      <div ref={chartContainerRef} />
    </div>
  );
};

export default CandlestickChart;
