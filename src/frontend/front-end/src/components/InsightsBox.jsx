'use client'
import React, { useState } from 'react'

const InsightButton = ({header}) => {
    return (
        <button type="button" className="flex flex-col items-center w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl p-4 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
            <h5 className="mb-2 text-2xl font-normal tracking-tight text-gray-900 dark:text-white">
                {header}
            </h5>
            <p className="mb-3 font-normal text-gray-700 dark:text-gray-400"></p>
        </button>
    )
}

const InsightsBox = () => {
    const [activeTab, setActiveTab] = useState('insightsSetOne')

    const insightsData = {
        insightsSetOne: ['AI Generated Prompt Header 1', 'AI Generated Prompt Header 2', 'AI Generated Prompt Header 3', 'AI Generated Prompt Header 4'],
        insightsSetTwo: ['AI Generated Prompt Header 5', 'AI Generated Prompt Header 6', 'AI Generated Prompt Header 7', 'AI Generated Prompt Header 8'],
        insightsSetThree: ['AI Generated Prompt Header 9', 'AI Generated Prompt Header 10', 'AI Generated Prompt Header 11', 'AI Generated Prompt Header 12']
    };

    const tabs = Object.keys(insightsData).map((tabId, index) => ({
        id: tabId,
        title: (index + 1).toString()
    }));

    const handleTabClick = (tabId) => {
        setActiveTab(tabId)
    }

    return (
        <div className="p-4 w-full">
            <div className="flex justify-between items-center bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                <div className="flex flex-col justify-between p-4 leading-normal">
                    <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                        Insights
                    </h5>
                </div>
                <div className="mb-4 border-b border-gray-200 dark:border-gray-700">
                    <ul className="flex flex-wrap -mb-px text-sm font-medium text-center" id="default-tab" role="tablist">
                        {tabs.map(tab => (
                            <li className="me-2" role="presentation" key={tab.id}>
                                <button className="inline-block p-4 border-b-2 rounded-t-lg" id={`${tab.id}-tab`} type="button" role="tab" aria-controls={tab.id} aria-selected={activeTab === tab.id} onClick={() => handleTabClick(tab.id)}>
                                    {tab.title}
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
                <button type="button" className="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-full text-sm px-5 py-2.5 text-center inline-flex items-center me-2 dark:text-gray-800 dark:bg-white dark:hover:bg-gray-300 dark:focus:ring-gray-700 dark:border-gray-700">
                    Refresh
                </button>
            </div>
            {Object.entries(insightsData).map(([key, values]) => (
                activeTab === key && (
                    <div key={key}>
                        {values.map((header, index) => (
                            <InsightButton key={index} header={header} />
                        ))}
                    </div>
                )
            ))}
        </div>
    )
}

export default InsightsBox
