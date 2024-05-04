import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

const SeriesChart = ({ selectedName, selectedInterval }) => {
  const chartContainerRef = useRef();
  const [seriesdata, setSeriesData] = useState([]);
  const [lineData, setLineData] = useState([]);
  const [lineDataLSTM, setLineDataLSTM] = useState([]);
  const [lineDataGCN, setLineDataGCN] = useState([]);

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
        const stockName = selectedName;
        const interval = selectedInterval;

        const response = await fetch(
          `http://localhost:8080/get-stock/${stockName}/${interval}`
        );
        const rawData = await response.json();

        const lineResponse = await fetch(`http://localhost:8080/get-prediction/${stockName}`);
        const lineRawData = await lineResponse.json();

        const lineResponseLSTM = await fetch(`http://localhost:8080/get-prediction-LSTM/${stockName}`);
        const lineRawDataLSTM = await lineResponseLSTM.json();

        const lineResponseGCN = await fetch(`http://localhost:8080/get-prediction-GCN/${stockName}`);
        const lineRawDataLGCN = await lineResponseGCN.json();
        
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

          if (Array.isArray(lineRawData)) {
            const transformedLineData = lineRawData.map((item) => ({
              time: new Date(item.index).toISOString().split("T")[0],
              value: typeof item.close === "number" ? item.close : 0
            }));
            transformedLineData.sort((a, b) => new Date(a.time) - new Date(b.time));
            setLineData(transformedLineData);
          } else {
            console.error("Invalid data structure received for line data:", lineRawData);
          }

          if (Array.isArray(lineRawDataLSTM)) {
            const transformedLineData = lineRawDataLSTM.map((item) => ({
              time: new Date(item.index).toISOString().split("T")[0],
              value: typeof item.close === "number" ? item.close : 0
            }));
            setLineDataLSTM(transformedLineData);
          } else {
            console.error("Invalid data structure received for line data:", lineRawData);
          }

          if (Array.isArray(lineRawDataLGCN)) {
            const transformedLineData = lineRawDataLGCN.map((item) => ({
              time: new Date(item.index).toISOString().split("T")[0],
              value: typeof item.close === "number" ? item.close : 0
            }));
            setLineDataGCN(transformedLineData);
          } else {
            console.error("Invalid data structure received for line data:", lineRawData);
          }



        } else {
          console.error("Invalid data structure received for series data:", rawData);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, [selectedName, selectedInterval]); 

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, chartOptions);

    const lineSeries = chart.addLineSeries({ color: "green", lineWidth: 2 });
    lineSeries.setData(seriesdata);

    const lineSeries_pred = chart.addLineSeries({ color: 'orange', lineWidth: 3 });
    lineSeries_pred.setData(lineData);

    const lineSeries_pred_LSTM = chart.addLineSeries({ color: 'blue', lineWidth: 3 });
    lineSeries_pred_LSTM.setData(lineDataLSTM);

    const lineSeries_pred_GCN = chart.addLineSeries({ color: 'brown', lineWidth: 3 });
    lineSeries_pred_GCN.setData(lineDataGCN);

    chart.timeScale().fitContent();

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [seriesdata, lineData,lineDataLSTM,lineDataGCN]);

  return <div ref={chartContainerRef} />;
};

export default SeriesChart;
