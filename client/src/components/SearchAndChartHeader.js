import React, { useState, useEffect } from "react";
import CandlestickChart from "./chart";

const SearchAndChartHeader = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [names, setNames] = useState([]);
  const [selectedName, setSelectedName] = useState("RELIANCE.NS");
  const [suggestedNames, setSuggestedNames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
 

  useEffect(() => {
    setLoading(true);
    // Fetch names from your API endpoint
    fetch("/get-all-names")
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
      // Fetch names based on the search term
      fetch(`/get-names/${searchTerm}`)
        .then((response) => response.json())
        .then((data) => {
          setSuggestedNames(data);
          setLoading(false);
        })
        .catch((error) => {
          console.error("Error fetching suggested names:", error);
          setError("Error fetching suggested names. Please try again.");
          setLoading(false);
        });
    }, 300); // Adjust the delay as needed

    // Cleanup function to clear the timeout
    return () => {
      clearTimeout(timeoutId);
    };
  }, [searchTerm]);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSelect = (name) => {
    setSelectedName(name);
  };

  return (
    <div className="flex bg-green-300 text-green-700 font-bold justify-between">
      <div className="mx-2">
        {/* Search Bar */}
        <input
          type="text"
          placeholder="Search names..."
          value={searchTerm}
          onChange={handleSearch}
        />

        {/* Display matched names in the dropdown */}
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}
        {!loading && !error && (
          <ul>
            {suggestedNames.map((matchedName) => (
              <li key={matchedName} onClick={() => handleSelect(matchedName)}>
                {matchedName}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Candlestick Chart */}
      {selectedName && <CandlestickChart selectedName={selectedName || "RELIANCE.NS"} />}
    </div>
  );
};

export default SearchAndChartHeader;
