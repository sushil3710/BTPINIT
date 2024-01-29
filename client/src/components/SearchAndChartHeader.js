import React, { useState, useEffect } from "react";
import CandlestickChart from "./chart";
import SelectSearch from 'react-select-search';

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
  


  return (
     <div className="flex flex-col items-center bg-green-200 text-green-700 font-bold" style={{ height: "80px" }}>
      {/* <SelectSearch options={names} value="sv" name="language" placeholder="Choose your language" /> */}
      <div className="m-7">
        {/* Search Bar */}
        <input
          type="text"
          placeholder="Search names..."
          value={searchTerm}
          onChange={handleSearch}
          className="border rounded py-2 px-4 focus:outline-none focus:border-blue-500"
        />

        {/* Display names in the dropdown */}
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

      {/* Candlestick Chart */}
      {<CandlestickChart selectedName={selectedName} />}
    </div>
  );
};

export default SearchAndChartHeader;
