'use client'
import React, { useState, useContext, useEffect } from 'react'
import { SelectedColumnContext } from '../context/SelectedColumnContext'
// useEffect here to detect change in the selected value in dropdown
// takes in the column name selected by the user

const InsightButton = ({header}) => {
    return (
        <div className="px-4 py-2">
            <button type="button" className="flex flex-col w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl p-4 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
            <h5 className="text-lg tracking-tight text-gray-900 dark:text-white">
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
    const [activeTab, setActiveTab] = useState(0);
    const itemsTab = 3;

    useEffect(() => {
        if (selectedColumn === undefined || selectedColumn === null || selectedColumn === '') {
            return;
        }
        const getInsightsData = async (column_name, prev_insights) => {
            console.log("?this is the selected column", column_name);
            try {
                const response = await fetch('http://127.0.0.1:8080/get_insights', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({column_name, prev_insights}),
                });
                const data = await response.json();
                // Check if the response is ok
                if (response.ok) {
                    const insightsData = data.insights;
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

    // useEffect(() => {
    //     if (Object.keys(insightsData).length > 0) {
    //         setActiveTab(Object.keys(insightsData)[0]);
    //     }
    // }, [insightsData]);

    // const tabs = Object.keys(insightsData).map((tabId, index) => ({
        //     id: tabId,
        //     title: (index + 1).toString()
        // }));
        
    console.log("this is the insights data", insightsData);
    // Assuming insightsData is an array of strings
    const insightsDataSplit = [];
    for (let i = 0; i < insightsData.length; i += itemsTab) {
        insightsDataSplit.push(insightsData.slice(i, i + itemsTab));
    }

    console.log("This is the split data: ", insightsDataSplit);
    const handleTabClick = (index) => {
        setActiveTab(index);
    };

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
                        {insightsDataSplit.map((_, index) => (
                            <li key={index} role="presentation">
                                <button
                                    className={`button-styles ${activeTab === index ? 'active-styles' : ''}`}
                                    onClick={() => handleTabClick(index)}
                                >
                                    Tab {index + 1}
                                </button>
                            </li>
                        ))}
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
            <div className="overflow-auto" style={{ height: '300px' }}>
                {insightsDataSplit[activeTab]?.map((header, index) => (
                        <InsightButton key={index} header={header} />
                    ))}
            </div>
        </div>
    )
}

export default InsightsBox


            {/* {insightsData?.map(([key, values]) => (
                activeTab === key && (
                    <div key={key}>
                        {values.map((header, index) => (
                            <InsightButton key={index} header={header} />
                        ))}
                    </div>
                )
            ))} */}