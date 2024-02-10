import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

const SeriesChart = ({ selectedName, selectedInterval }) => {
  const chartContainerRef = useRef();

  const [seriesdata, setSeriesData] = useState([]);
  const chartOptions = {
    layout: {
      textColor: "black",
      background: { type: "solid", color: "white" },
    },
    width: window.innerWidth,
    height: window.innerHeight - 100,
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        let stockName = selectedName;
        let interval = selectedInterval;

        const response = await fetch(
          `http://localhost:8080/get-stock/${stockName}/${interval}`
        );
        const rawData = await response.json();
        const lineResponse = await fetch(`http://localhost:8080/get-prediction/${stockName}`);
        const lineRawData = await lineResponse.json();
        

        if (Array.isArray(rawData)) {
          const transformedData = rawData.map((item) => {
            const value = typeof item.close === "number" ? item.close : 0;
            const formattedDate = new Date(item.index).toISOString().split("T")[0];
            return {
              time: formattedDate,
              value,
            };
          });
          setSeriesData(transformedData);

         
        } else {
          console.error("Invalid data structure received:", rawData);
        }
      } catch (error) {
        console.error("Error fetching candlestick data:", error);
      }
    };
    fetchData();
  }, [selectedName, selectedInterval]); // Include selectedName and selectedInterval in the dependency array

  useEffect(() => {
    // Check if candlestickData is not empty before rendering the chart
    const chart = createChart(chartContainerRef.current, chartOptions);
    const lineSeries = chart.addLineSeries({ color: "#2962FF" });
    lineSeries.setData(seriesdata);

    chart.timeScale().fitContent();

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [seriesdata]);

  return <div ref={chartContainerRef} />;
};

export default SeriesChart;
