'use client';

import React, { useState } from 'react';

export const InsightsDataContext = React.createContext({
  insightsData: '',
  updateInsightsData: () => {},
  selectedInsights: [],
  updateSelectedInsights: () => {},
});

export function InsightsDataProvider({ children }) {
  const [insightsData, updateInsightsData] = useState({});
  const [selectedInsights, setSelectedInsights] = useState([]);

  const updateSelectedInsights = (newInsight) => {
    if (selectedInsights.includes(newInsight)) {
      const deSelectedInsights = selectedInsights.filter((insights) => insights !== newInsight);
      setSelectedInsights(deSelectedInsights);
    } else {
      const selectedInsightsList = [...selectedInsights, newInsight];
      setSelectedInsights(selectedInsightsList);
    }
  };

  return (
    <InsightsDataContext.Provider
      value={{
        insightsData, updateInsightsData, selectedInsights, updateSelectedInsights,
      }}
    >
      {children}
    </InsightsDataContext.Provider>
  );
}
