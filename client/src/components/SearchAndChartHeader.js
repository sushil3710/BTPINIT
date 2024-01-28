import React, { useState, useEffect } from "react";
import CandlestickChart from "./chart";
import axios from "axios";

const SearchAndChartHeader = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [names, setNames] = useState([]);
  const [selectedName, setSelectedName] = useState("");
  const [suggestedNames, setSuggestedNames] = useState([]);

  useEffect(() => {
    const fetchAllNames = async () => {
      try {
        const response = await axios.get("/get-all-names");
        setNames(response.data);
      } catch (error) {
        console.error("Error fetching names:", error);
      }
    };

    fetchAllNames();
  }, []);

  useEffect(() => {
    const debouncedFetchNames = async () => {
      const timeoutId = setTimeout(async () => {
        try {
          const response = await axios.get(`/get-names/${searchTerm}`);
          setSuggestedNames(response.data);
        } catch (error) {
          console.error("Error fetching suggested names:", error);
        }
      }, 300); // Adjust the delay as needed

      return () => clearTimeout(timeoutId);
    };

    debouncedFetchNames();
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
        <ul>
          {suggestedNames.map((matchedName) => (
            <li key={matchedName} onClick={() => handleSelect(matchedName)}>
              {matchedName}
            </li>
          ))}
        </ul>
      </div>

      {/* Candlestick Chart */}
      {selectedName && <CandlestickChart selectedName={selectedName} />}
    </div>
  );
};

export default SearchAndChartHeader;
