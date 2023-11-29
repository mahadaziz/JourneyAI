'use client'
import React, { useState, useContext, useEffect } from 'react'
import { SelectedColumnContext } from '../context/SelectedColumnContext'
// useEffect here to detect change in the selected value in dropdown
// takes in the column name selected by the user

const InsightButton = ({header}) => {
    return (
        <div className="px-4 py-2">
            <button type="button" className="flex flex-col items-center w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl p-4 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
            <h5 className="text-xl tracking-tight text-gray-900 dark:text-white">
                {header}
            </h5>
            <p className="mb-3 font-normal text-gray-700 dark:text-gray-400"></p>
            </button>
        </div>
    )
}

const InsightsBox = () => {
    const { selectedColumn } = useContext(SelectedColumnContext);
    const [insightsData, setInsightsData] = useState([]);
    const [previousInsights, setPreviousInsights] = useState([]);
    // const [activeTab, setActiveTab] = useState('insightsSetOne');

    useEffect(() => {
        const getInsightsData = async (selectedColumn, previousInsights) => {
            try {
                const response = await fetch('http://127.0.0.1:8080/get_insights', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({selectedColumn, previousInsights}),
                });
                const data = await response.json();
                console.log("Data in frontend: ", data)
                // Check if the response is ok
                if (response.ok) {
                    const insightsData = data.insights;
                    console.log("what is this", data);
                    const previousData = data.prev_insights;
                    setInsightsData(insightsData);
                    setPreviousInsights(previousData);
                } else {
                    // Handle HTTP errors
                    console.error('Failed to fetch insightsData: ', data);
                }
            } catch (error) {
                // Handle network errors
                console.error('Network error:', error);
            }
        };
        getInsightsData(selectedColumn, previousInsights);
    }, [selectedColumn]);

    // insightsData = {
    //     insightsSetOne: ['AI Generated Prompt Header 1', 'AI Generated Prompt Header 2', 'AI Generated Prompt Header 3', 'AI Generated Prompt Header 4'],
    //     insightsSetTwo: ['AI Generated Prompt Header 5', 'AI Generated Prompt Header 6', 'AI Generated Prompt Header 7', 'AI Generated Prompt Header 8'],
    //     insightsSetThree: ['AI Generated Prompt Header 9', 'AI Generated Prompt Header 10', 'AI Generated Prompt Header 11', 'AI Generated Prompt Header 12']
    // };

    console.log(insightsData);
    console.log(previousInsights);
    // const tabs = Object.keys(insightsData).map((tabId, index) => ({
    //     id: tabId,
    //     title: (index + 1).toString()
    // }));

    const handleTabClick = (tabId) => {
        setActiveTab(tabId)
    }

    return (
        <div className="py-4 px-2 w-full">
            <div className="flex justify-between items-center bg-neutral-900 border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                <div className="flex flex-col justify-between p-4 leading-normal">
                    <h5 className="mb-2 text-2xl font-bold tracking-tight text-white dark:text-white">
                        Insights
                    </h5>
                </div>
                <div className=" border-gray-200 dark:border-gray-700">
                    <ul className="flex flex-wrap -mb-px text-md font-medium text-center " id="default-tab" role="tablist">
                        {/* {tabs.map(tab => (
                            <li className="me-6 " role="presentation" key={tab.id}>
                                <button className="flex justify-center items-center h-[40px] w-[20px] p-4 rounded-lg text-white bg-gray-600 hover:bg-gray-400" id={`${tab.id}-tab`} type="button" role="tab" aria-controls={tab.id} aria-selected={activeTab === tab.id} onClick={() => handleTabClick(tab.id)}>
                                    {tab.title}
                                </button>
                            </li>
                        ))} */}
                    </ul>
                </div>
                <button type="button" className="text-white bg-gray-600 hover:bg-gray-400 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-full text-sm px-5 py-2.5 text-center inline-flex items-center me-2 dark:text-gray-800 dark:bg-white dark:hover:bg-gray-300 dark:focus:ring-gray-700 dark:border-gray-700">
                    Refresh
                </button>
            </div>
            {/* {Object.entries(insightsData).map(([key, values]) => (
                activeTab === key && (
                    <div key={key}>
                        {values.map((header, index) => (
                            <InsightButton key={index} header={header} />
                        ))}
                    </div>
                )
            ))} */}
        </div>
    )
}

export default InsightsBox
