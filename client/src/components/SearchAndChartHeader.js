import React, { useState, useEffect } from "react";
import CandlestickChart from "./chart";

const SearchAndChartHeader = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [names, setNames] = useState([]);
  const [selectedName, setSelectedName] = useState("RELIANCE.NS");
  const [suggestedNames, setSuggestedNames] = useState([]);
  const [selectedInterval, setSelectedInterval] = useState("1day"); // Default interval is 1day
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      setSuggestedNames(filteredNames);
      setLoading(false);
    }, 300); // Adjust the delay as needed

    // Cleanup function to clear the timeout
    return () => {
      clearTimeout(timeoutId);
    };
  }, [searchTerm, names]);

  const handleSearch = (event) => {
    const newSearchTerm = event.target.value;
    setSearchTerm(newSearchTerm);
    setError(null); // Clear the error when a new search term is entered

    // Set suggestions only if the search term is not empty
    if (newSearchTerm.trim() !== "") {
      setSuggestedNames(
        names.filter((name) => name.toLowerCase().includes(newSearchTerm.toLowerCase()))
      );
    } else {
      setSuggestedNames([]); // Clear suggestions when the search term is empty
    }
  };

  const handleSelect = (selectedName) => {
    const originalName = names.find(name => name.toLowerCase() === selectedName.toLowerCase());
    console.log("Selected Name:", originalName);
    setSelectedName(originalName);
    setSuggestedNames([]); // Clear suggestions when a name is selected
  };

  const handleIntervalSelect = (selectedInterval) => {
    setSelectedInterval(selectedInterval);
  };

  return (
    <div className="flex flex-col items-center bg-blue-100 text-green-700 font-bold" style={{ height: "100px" }}>
      <div className="flex m-7">
        <div>
          <input
            type="text"
            placeholder="Search names..."
            value={searchTerm}
            onChange={handleSearch}
            className="border rounded py-2 px-4 focus:outline-none focus:border-blue-500"
          />
          {suggestedNames.length > 0 && (
            <ul className="list-none absolute bg-white w-48 border rounded mt-1 overflow-y-auto max-h-32">
              {suggestedNames.map((matchedName) => (
                <li
                  key={matchedName}
                  onClick={() => handleSelect(matchedName)}
                  className="cursor-pointer hover:bg-gray-200 py-1 px-2"
                >
                  {matchedName}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="ml-4">
          <label htmlFor="intervalDropdown" className="mr-2">Select Interval:</label>
          <select
            id="intervalDropdown"
            value={selectedInterval}
            onChange={(e) => handleIntervalSelect(e.target.value)}
          >
            <option value="1day">1 Day</option>
            <option value="1week">1 Week</option>
            <option value="1month">1 Month</option>
            <option value="1year">1 Year</option>
          </select>
        </div>
      </div>

      <div style={{ height: "400px", width: "100%" }}>
        <CandlestickChart selectedName={selectedName} timep={selectedInterval} />
      </div>
    </div>
  );
};

export default SearchAndChartHeader;
