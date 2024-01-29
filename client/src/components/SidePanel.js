import React, { useState } from "react";

const SidePanel = () => {
  const [isSidePanelOpen, setIsSidePanelOpen] = useState(false);

  const toggleSidePanel = () => {
    setIsSidePanelOpen(!isSidePanelOpen);
  };

  return (
    <div className="bg-gray-50  ">
      <ul className="flex flex-col space-y-8  mx-8 p-4 overflow-hidden z-10">
        <li> FUTURES </li>
        <li> OPTIONS </li>
        <li> STRATEGY </li>
        <li> BACKTEST </li>
        <li> ABOUT </li>
      </ul>
    </div>
  );
};

export default SidePanel;
