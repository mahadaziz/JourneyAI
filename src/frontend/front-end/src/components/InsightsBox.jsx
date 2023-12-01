'use client'
import React, { useState, useContext, useEffect } from 'react';
import { SelectedColumnContext } from '../context/SelectedColumnContext';
import { HypothesisDataContext } from '../context/HypothesisDataContext';
import { motion } from "framer-motion";
import '../styles/insights.css';

const variants = {
    // fade upwards
    // hidden: { opacity: 0, y: 30 },
    // visible: { opacity: 1, y: 0 }
    //Zoom in 
    // hidden: { opacity: 0, scale: 0.8 },
    // visible: { opacity: 1, scale: 1 }
    // slide in left
    // hidden: { opacity: 0, x: -100 },
    // visible: { opacity: 1, x: 0 }
    // bounce in variatns
    // hidden: { opacity: 0, scale: 0.6 },
    // visible: { opacity: 1, scale: 1, transition: { type: "spring", damping: 20, stiffness: 300 } }
    // flip in
    hidden: { opacity: 0, rotateX: 90 },
    visible: { opacity: 1, rotateX: 0 }
    //fade  in scale
    // hidden: { opacity: 0, scale: 0.9 },
    // visible: { opacity: 1, scale: 1 }
}

const buttonVariants = {
    hover: { backgroundColor: "#9ca3af" }, // Example hover background color
    clicked: { scale: 0.9, backgroundColor: "#f3f4f6" },  // Example: slightly scale down when clicked
    normal: { scale: 1, backgroundColor: "#FFFFFF"}
};

const InsightButton = ({header}) => {
    return (
        <motion.div 
            className="px-4 py-2"
            initial="hidden"  // Initial state before animation
            animate="visible" // State to animate to
            variants={variants} // Animation variants
            transition={{ duration: 0.5 }} // Transition properties>
        >
            <button type="button" className="flex flex-col p-3 items-center w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
            <h5 className="text-lg text-left tracking-tight text-gray-900 dark:text-white">
                {header}
            </h5>
            <p className="mb-3 font-normal text-gray-700 dark:text-gray-400"></p>
            </button>
        </motion.div>
    )
}

const InsightsBox = () => {
    const { selectedColumn } = useContext(SelectedColumnContext);
    const { hasHypothesisData } = useContext(HypothesisDataContext);
    console.log(hasHypothesisData);
    const [insightsData, setInsightsData] = useState([]);
    const [previousInsights, setPreviousInsights] = useState([]);
    const [refresh, setRefresh] = useState(false);
    const [activeTab, setActiveTab] = useState(0);
    const itemsTab = 6;

    useEffect(() => {
        if (selectedColumn === undefined || selectedColumn === null || selectedColumn === '') {
            return;
        }
        const getInsightsData = async (column_name, prev_insights, insight_count) => {
            try {
                const response = await fetch('http://127.0.0.1:8080/get_insights', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'column_name':column_name, 'prev_insights':prev_insights, 'insight_count':insight_count}),
                });
                const data = await response.json();
                if (response.ok) {
                    const insightsData = data.insights;
                    const previousData = data.prev_insights;
                    setInsightsData(insightsData);
                    setPreviousInsights(previousData);
                } else {
                    console.error('Failed to fetch insightsData: ', data);
                }
            } catch (error) {
                console.error('Network error:', error);
            }
        };
        getInsightsData(selectedColumn, previousInsights, 18);
    }, [selectedColumn, refresh]);

    // insightsData is an array of strings
    const insightsDataSplit = [];
    for (let i = 0; i < insightsData.length; i += itemsTab) {
        insightsDataSplit.push(insightsData.slice(i, i + itemsTab));
    }

    console.log("This is the split data: ", insightsDataSplit);
    const handleTabClick = (index) => {
        setActiveTab(index);
    };

    const handleRefresh = () => {
        setRefresh(prev => !prev); // Flip the state to trigger re-fetch
    };

    const getKey = (index) => `${selectedColumn}-${activeTab}-${index}`;

    return (
        <div className="py-4 px-8 w-full">
            <div className="flex justify-between items-center bg-neutral-900 border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                <div className="flex flex-col justify-between p-3 leading-normal">
                    <h5 className="mb-2 text-2xl font-bold tracking-tight text-white dark:text-white">
                        Insights
                    </h5>
                </div>
                <div className=" border-gray-200 dark:border-gray-700">
                    <ul className="flex flex-wrap -mb-px text-md font-medium text-center " id="default-tab" role="tablist">
                        {insightsDataSplit.map((_, index) => (
                            <li className="me-6" key={index} role="presentation">
                                <motion.button
                                    className={`flex justify-center items-center h-[40px] w-[20px] p-4 rounded-lg text-black bg-white hover:bg-gray-400 ${activeTab === index ? 'active-styles' : ''}`}
                                    onClick={() => handleTabClick(index)}
                                    variants={buttonVariants}
                                    whileHover="hover"
                                    whileTap="clicked"  // This applies the 'clicked' variant while the button is being tapped/clicked
                                    initial="normal"
                                    transition={{ duration: 0.2 }}
                                >
                                    {index + 1}
                                </motion.button>
                            </li>
                        ))}
                    </ul>
                </div>
                <motion.button 
                    onClick={handleRefresh} 
                    type="button" 
                    className="text-black bg-white hover:bg-gray-400 focus:outline-none font-medium rounded-full text-sm px-5 py-2.5 text-center inline-flex items-center me-2 dark:text-gray-800 dark:bg-white dark:hover:bg-gray-300"
                    variants={buttonVariants}
                    whileHover="hover"
                    whileTap="clicked"  // This applies the 'clicked' variant while the button is being tapped/clicked
                    initial="normal"
                    transition={{ duration: 0.2 }}
                >    
                    Refresh
                </motion.button>
            </div>
            {insightsData.length > 0 ? (
                <div className={hasHypothesisData ? "insightScroll" : "insightScrollFull insightScrollWheel"}>   
                    {insightsDataSplit[activeTab]?.map((header, index) => (
                            <div className="insightButton"  key={`${getKey(index)}-${refresh}`}>
                                <InsightButton header={header} />
                            </div>
                        ))}
                </div>
            ) : (
                <div className="text-center p-4 font-medium">
                    Select a topic to view insights.
                </div>
            )}
        </div>
    )
}

export default InsightsBox