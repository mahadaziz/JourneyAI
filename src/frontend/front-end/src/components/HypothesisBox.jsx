'use client'
import React, { useState, useEffect, useContext } from 'react';
import PopupModal from './PopupModal';
import { ChartBarIcon } from '@heroicons/react/24/solid';
import { SelectedColumnContext } from '../context/SelectedColumnContext';
import { HypothesisDataContext } from '../context/HypothesisDataContext';
import { Tooltip } from 'react-tooltip';
import { motion } from "framer-motion"
import '../styles/hypothesis.css';

const variants = {
    hidden: { opacity: 0, rotateX: 90 },
    visible: { opacity: 1, rotateX: 0 }
}

// framer motion transitions for buttons
const buttonVariants = {
    hover: { backgroundColor: "#9ca3af" }, // Example hover background color
    clicked: { scale: 0.9, backgroundColor: "#f3f4f6" },  // Example: slightly scale down when clicked
    normal: { scale: 1, backgroundColor: "#FFFFFF"}
};

const HypothesisBox = () => {
    const { selectedColumn } = useContext(SelectedColumnContext);
    const { updateHypothesisData } = useContext(HypothesisDataContext);
    const [hypothesisData, setHypothesisData] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [refresh, setRefresh] = useState(false);

    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);
    
    const getHypothesisData = async () => {
        if (!selectedColumn) return;

        try {
            const response = await fetch('http://127.0.0.1:8080/get_hypothesis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'column_name': selectedColumn }),
            });
            const data = await response.json();
            if (response.ok) {
                setHypothesisData(data.data);
                if (data.data.length > 0) {
                    updateHypothesisData(true);
                }
                else {
                    updateHypothesisData(false);
                }
            } else {
                console.error('Failed to fetch hypothesisData: ', data);
            }
        } catch (error) {
            console.error('Network error:', error);
        }
    };

    useEffect(() => {
        getHypothesisData();
    }, [selectedColumn, refresh]);

    const handleRefresh = () => {
        setRefresh(prev => !prev); // Flip the state to trigger re-fetch
    };
    return (
        
        <div className="px-8 w-full">
            <Tooltip id="my-tooltip" content="Open Graph" style={{ zIndex: 1 }}/>
            <div className="flex justify-between items-center bg-neutral-900 border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                <div className="flex flex-col justify-between p-3 leading-normal">
                    <h5 className="mb-2 text-2xl font-bold tracking-tight text-white dark:text-white">
                        Hypotheses
                    </h5>
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
            {selectedColumn === undefined || selectedColumn === null || selectedColumn === ''? (
                <div className="text-center p-4 font-medium">
                    Select a topic to view hypotheses.
                </div>
                ) : hypothesisData.length > 0 ? (
                    <div className="hypothesisScroll">
                        {hypothesisData.map((header, index) => (
                            // <HypothesisButton key={index} header={header} />
                            <motion.div key={`${header}-${refresh}`} 
                                className="relative px-4 py-2"
                                initial="hidden"
                                animate="visible"
                                variants={variants}
                                transition={{ duration: 0.5 }}>
                                <div className="flex items-center justify-between w-full p-3 bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                                    <h5 className="text-lg text-left font-normal tracking-tight text-gray-900 dark:text-white">
                                        {header}
                                    </h5>
                                    <div className="absolute bottom-0 right-0 p-6">
                                        <ChartBarIcon onClick={openModal} 
                                                    className="h-6 w-6 cursor-pointer text-gray-500 hover:text-gray-700 dark:hover:text-gray-300" aria-label="Open modal"
                                                    data-tooltip-id="my-tooltip" data-tooltip-content="View Graph" data-tooltip-place="left"
                                        />
                                    </div>
                                    <PopupModal isModalOpen={isModalOpen} closeModal={closeModal} />
                                </div>
                            </motion.div> 
                        ))}
                    </div>   
                ) : (
                <div className="text-center p-4 font-medium">
                    No data available.
                </div>
            )}
        </div>
    )
}

export default HypothesisBox
 {/* flex-shrink-0 */}
                {/* <ChartBarIcon onClick={openModal} className="flex-shrink-0 h-6 w-6 cursor-pointer text-gray-500 hover:text-gray-700 dark:hover:text-gray-300" aria-label="Open modal" /> */}
