import React, { useState, useEffect } from "react";
import CandlestickChart from "./chart";
import SeriesChart from "./SeriesChart";
import myimage from "../images/logodark.svg";
import SidePanel from "./SidePanel";
const SearchAndChartHeader = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [names, setNames] = useState([]);
  const [selectedName, setSelectedName] = useState("RELIANCE.NS");
  const [suggestedNames, setSuggestedNames] = useState([]);
  const [selectedInterval, setSelectedInterval] = useState("5years"); // Default interval is 1day
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSidePanelOpen, setIsSidePanelOpen] = useState(false);

  const toggleSidePanel = () => {
    setIsSidePanelOpen(!isSidePanelOpen);
  };
  const [chartType, setchartType] = useState("candlesticks");

  useEffect(() => {
    setLoading(true);
    // Fetch names from your API endpoint
    fetch("http://localhost:8080/get-all-names")
      .then((response) => response.json())
      .then((data) => {
        setNames(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching names:", error);
        setError("Error fetching names. Please try again.");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    setLoading(true);
    // Debouncing the API call for better performance
    const timeoutId = setTimeout(() => {
      // Filter names based on the search term
      const filteredNames = names.filter((name) =>
        name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      // setSuggestedNames(filteredNames);
      setLoading(false);
    }, 300); // Adjust the delay as needed

    // Cleanup function to clear the timeout
    return () => {
      clearTimeout(timeoutId);
    };
  }, [searchTerm, names]);

  const handlecharttype = (selectedcharttype) => {
    setchartType(selectedcharttype);
  };

  const handleSearch = (event) => {
    const newSearchTerm = event.target.value;
    setSearchTerm(newSearchTerm);
    setError(null); // Clear the error when a new search term is entered

    // Set suggestions only if the search term is not empty
    if (newSearchTerm === "") {
      setSuggestedNames([]);
    } else if (newSearchTerm.trim() !== "") {
      let trimmedsearchnames = names.filter((name) =>
        name.toLowerCase().includes(newSearchTerm.toLowerCase())
      );
      setSuggestedNames(trimmedsearchnames.slice(0, 10));
    } else {
      setSuggestedNames([]); // Clear suggestions when the search term is empty
    }
  };

  const handleSelect = (selectedName) => {
    const originalName = names.find(
      (name) => name.toLowerCase() === selectedName.toLowerCase()
    );
    console.log("Selected Name:", originalName);
    setSelectedName(originalName);
    setSuggestedNames([]); // Clear suggestions when a name is selected
  };

  const handleIntervalSelect = (selectedInterval) => {
    setSelectedInterval(selectedInterval);
  };

  return (
    <div className="flex flex-col items-center  text-black-700   ">
      <div className="flex m-5 justify-between items-center ">
        <div
          onClick={toggleSidePanel}
          className={`md:w-64 w-56   ${isSidePanelOpen ? "block" : "hidden"}`}
          style={{position: "fixed",
          top: 0,
          left: 0, // Adjust this value to move the panel more to the left
          width: "fit-content",
          height: "100vh",
          zIndex: 1000,}}
        >
          <SidePanel></SidePanel>
        </div>

        <div>
          <ul
            onClick={toggleSidePanel}
            className={` flex rotate-90 mr-48 text-3xl   ${
              !isSidePanelOpen ? "block" : "hidden"
            }`}
          >
            <li>|</li>
            <li>|</li>
            <li>|</li>
          </ul>
        </div>
        <div className="mr-24 ">
          <img src={myimage} alt="" />
        </div>
        <div>
          <input
            type="text"
            placeholder="Search names..."
            value={searchTerm}
            onChange={handleSearch}
            className="border rounded py-2 px-4 focus:outline-none focus:border-black-500"
          />
          {suggestedNames.length > 0 && (
            <ul className="list-none absolute bg-white w-48 border rounded mt-1   overflow-hidden z-10">
              {suggestedNames.map((matchedName) => (
                <li
                  key={matchedName}
                  onClick={() => handleSelect(matchedName)}
                  className="cursor-pointer hover:bg-gray-200 py-1 px-2"
                >
                  {matchedName.split(".")[0]}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="ml-4">
          <label htmlFor="intervalDropdown" className="mr-2">
            Select Interval:
          </label>
          <select
            className=" border-black border-2"
            id="intervalDropdown"
            value={selectedInterval}
            onChange={(e) => handleIntervalSelect(e.target.value)}
          >
            <option value="1day">1 Day</option>
            <option value="1week">1 Week</option>
            <option value="1month">1 Month</option>
            <option value="1year">1 Year</option>
            <option value="5years">5 Years</option>
          </select>
        </div>

        <div>
          <label htmlFor="intervalDropdown" className="ml-12 mr-2">
            Select Chart:
          </label>
          <select
            className=" text-black-700 p-1 px-2 rounded-sm  border-black border-2"
            id="chartDropdown"
            value={chartType}
            onChange={(e) => handlecharttype(e.target.value)}
          >
            <option value="candlesticks">candlesticks</option>
            <option value="linechart">LineChart</option>
          </select>
        </div>
      </div>

  <div className="stock-name"  style={{ fontWeight: 'bold', marginLeft: '10px' }}>{selectedName}</div>
  <div style={{ height: "80vh", width: "95%", overflow: "auto", marginLeft: "8px", marginRight: "1px",marginTop: "8px"}}>
  <div style={{ border: "2px solid #000", borderRadius: "8px", boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)", padding: "10px" }}>
    {chartType === "candlesticks" ? (
      <CandlestickChart
        selectedName={selectedName}
        selectedInterval={selectedInterval}
      />
    ) : (
      <SeriesChart
        selectedName={selectedName}
        selectedInterval={selectedInterval}
      />
    )}
  </div>
</div>

 </div>
  );
};

export default SearchAndChartHeader;
