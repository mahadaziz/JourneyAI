/* eslint-disable max-len */

'use client';

import React, {
  useState, useContext, useEffect, useRef,
} from 'react';
import { motion } from 'framer-motion';
import { ChartBarIcon } from '@heroicons/react/24/solid';
import PopupModal from './PopupModal';
import { SelectedColumnContext } from '../context/SelectedColumnContext';
import { HypothesisDataContext } from '../context/HypothesisDataContext';
import { InsightsDataContext } from '../context/InsightsDataContext';
import { ThumbsUp, ThumbsDown } from './Icons';
import '../styles/insights.css';

const variants = {
  hidden: { opacity: 0, rotateX: 90 },
  visible: { opacity: 1, rotateX: 0 },
};

const buttonVariants = {
  hover: { backgroundColor: '#9ca3af' }, // Example hover background color
  clicked: { scale: 0.9, backgroundColor: '#f3f4f6' }, // Example: slightly scale down when clicked
  normal: { scale: 1, backgroundColor: '#FFFFFF' },
};

function InsightButton({ option, header, array }) {
  const { selectedInsights, updateSelectedInsights } = useContext(InsightsDataContext);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);

  const openModal = (e) => {
    setModalData(array);
    e.stopPropagation();
    setIsModalOpen(true);
  };

  const closeModal = (e) => {
    e.stopPropagation();
    setIsModalOpen(false);
  };

  // Effect to handle cleanup or immediate actions upon modal closing
  useEffect(() => {
    if (!isModalOpen) {
      // Clear modal data immediately or after a delay if needed
      setModalData(null);
    }
  }, [isModalOpen]);

  const handleSelectedInsights = (newInsight) => {
    updateSelectedInsights(newInsight);
  };

  return (
    <motion.div
      className="px-4 py-1"
      initial="hidden" // Initial state before animation
      animate="visible" // State to animate to
      variants={variants} // Animation variants
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center">
        <button
          onClick={(() => handleSelectedInsights(header))}
          type="button"
          className={`relative flex-col p-3 items-center w-full border border-gray-200 rounded-lg shadow
          hover:bg-gray-200 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700 
          ${selectedInsights.includes(header) ? 'bg-violet-200 hover:bg-violet-300' : 'bg-white'
            }`}
        >
          <div className="flex flex-col items-center w-full">
            <h5 className="text-lg text-left tracking-tight text-gray-900 dark:text-white">
              {header}
            </h5>
            <p className="mb-3 font-normal text-gray-700 dark:text-gray-400" />
          </div>
          {option === 'graphs' && (
            <div className="absolute bottom-0 right-0 p-6">
              <ChartBarIcon
                onClick={openModal}
                className="h-6 w-6 cursor-pointer text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                aria-label="Open modal"
                data-tooltip-id="my-tooltip"
                data-tooltip-content="View Graph"
                data-tooltip-place="left"
              />
            </div>
          )}
          {isModalOpen && <PopupModal isModalOpen={isModalOpen} closeModal={closeModal} array={modalData} />}

        </button>
      </div>
    </motion.div>
  );
}

function InsightsBox({ datasetId }) {
  const { selectedColumn } = useContext(SelectedColumnContext);
  const { hasHypothesisData } = useContext(HypothesisDataContext);
  const { insightsData, updateInsightsData } = useContext(InsightsDataContext);
  const history = useRef({ column: null, values: [] });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [refresh, setRefresh] = useState(false);
  const [category, setSelectedOption] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const options = Object.keys(insightsData);
  const selectedOption = options.includes(category) ? category : options[0];
  const selectedData = Array.isArray(insightsData[selectedOption]) ? insightsData[selectedOption] : [];
  const graphData = selectedOption === 'graphs'
    ? Object.entries(insightsData.graphs).map(([description, array]) => ({ description, array }))
    : [];

  useEffect(() => {
    if (!selectedColumn) return undefined;
    const controller = new AbortController();
    const getInsights = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await fetch(`/api/datasets/${datasetId}/insights`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({
            column_name: selectedColumn,
            prev_insights: history.current.column === selectedColumn ? history.current.values : [],
            insight_count: 18,
          }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not load insights.');
        if (!controller.signal.aborted) {
          history.current = { column: selectedColumn, values: data.prev_insights };
          updateInsightsData(data.insights);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          updateInsightsData({});
          setError(err.message || 'Could not reach the analysis service.');
        }
      } finally {
        if (!controller.signal.aborted) setIsLoading(false);
      }
    };
    getInsights();
    return () => controller.abort();
  }, [datasetId, selectedColumn, refresh, updateInsightsData]);

  const toggleDropdown = () => setIsOpen(!isOpen);

  const handleSelect = (option) => {
    setSelectedOption(option);
    setIsOpen(false); // Close dropdown after selection
  };

  const handleRefresh = () => {
    setRefresh((prev) => !prev); // Flip the state to trigger re-fetch
  };

  // Function to handle click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownRef]);

  return (
    <div className="flex flex-col px-6 w-full">
      <div className="flex justify-between items-center bg-neutral-900 border border-gray-200 rounded-lg shadow dark:border-gray-700 dark:bg-[#030712]">
        <div className="flex flex-col justify-between p-3 leading-normal">
          <h5 className="mb-2 text-2xl font-bold tracking-tight text-white dark:text-white">
            Insights
          </h5>
        </div>
        <div className="border-gray-200 dark:border-gray-700">
          <div ref={dropdownRef}>
            <button
              type="button"
              onClick={toggleDropdown}
              className="relative focus:outline-none
              font-medium rounded-2xl px-3 py-2 border border-gray-700 text-center inline-flex items-center
              md:min-w-[100px] md:text-md lg:min-w-[200px]
              text-black bg-white hover:bg-gray-100 dark:bg-[#030712] dark:text-gray-200 dark:hover:bg-gray-800"
            >
              {selectedOption || 'Choose a category'}

              <svg className="w-2.5 h-2.5 ms-auto" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 4 4 4-4" />
              </svg>
            </button>

            {isOpen && (
              <div className="absolute z-10 w-[200px] bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800">
                <ul className="py-1">
                  {Object.keys(insightsData).map((key, index) => (
                    <li key={key}>
                      <button
                        type="button"
                        onClick={() => handleSelect(key)}
                        className="flex w-full justify-start px-4 py-2 rounded-lg text-sm hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-gray-200"
                      >
                        {key}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
        <motion.button
          onClick={handleRefresh}
          type="button"
          className="text-black bg-white hover:bg-gray-400 focus:outline-none font-medium rounded-full text-sm px-5 py-2.5 text-center inline-flex items-center me-2 dark:text-gray-800 dark:bg-white dark:hover:bg-gray-300"
          variants={buttonVariants}
          whileHover="hover"
          whileTap="clicked" // This applies the 'clicked' variant while the button is being tapped/clicked
          initial="normal"
          transition={{ duration: 0.2 }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 512 512">
            <path d="M105.1 202.6c7.7-21.8 20.2-42.3 37.8-59.8c62.5-62.5 163.8-62.5 226.3 0L386.3 160H352c-17.7 0-32 14.3-32 32s14.3 32 32 32H463.5c0 0 0 0 0 0h.4c17.7 0 32-14.3 32-32V80c0-17.7-14.3-32-32-32s-32 14.3-32 32v35.2L414.4 97.6c-87.5-87.5-229.3-87.5-316.8 0C73.2 122 55.6 150.7 44.8 181.4c-5.9 16.7 2.9 34.9 19.5 40.8s34.9-2.9 40.8-19.5zM39 289.3c-5 1.5-9.8 4.2-13.7 8.2c-4 4-6.7 8.8-8.1 14c-.3 1.2-.6 2.5-.8 3.8c-.3 1.7-.4 3.4-.4 5.1V432c0 17.7 14.3 32 32 32s32-14.3 32-32V396.9l17.6 17.5 0 0c87.5 87.4 229.3 87.4 316.7 0c24.4-24.4 42.1-53.1 52.9-83.7c5.9-16.7-2.9-34.9-19.5-40.8s-34.9 2.9-40.8 19.5c-7.7 21.8-20.2 42.3-37.8 59.8c-62.5 62.5-163.8 62.5-226.3 0l-.1-.1L125.6 352H160c17.7 0 32-14.3 32-32s-14.3-32-32-32H48.4c-1.6 0-3.2 .1-4.8 .3s-3.1 .5-4.6 1z" />
          </svg>
        </motion.button>
      </div>

      <div>
        {isLoading ? (
          <div className="flex justify-center items-center pt-12" role="status">
            <svg aria-hidden="true" className="inline w-8 h-8 text-black animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
              <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
            </svg>
            <span className="sr-only">Loading...</span>
          </div>
        ) : (
          <div>
            {(selectedData || graphData) && (selectedData?.length > 0 || graphData?.length > 0) ? (
              <div className={hasHypothesisData ? 'insightScroll' : 'insightScrollFull insightScrollWheel'}>
                {selectedOption === 'graphs' ? (
                  graphData.map((header, index) => (
                    <div key={index}>
                      <InsightButton option={selectedOption} header={header.description} array={header.array} />
                    </div>
                  ))
                ) : (
                  selectedData.map((header, index) => (
                    <div key={index}>
                      <InsightButton header={header} />
                    </div>
                  ))
                )}
              </div>
            ) : (
              <div className="text-center p-4 font-medium">
                {error || (selectedColumn ? 'No findings for this column.' : 'Select a column to view insights.')}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
export default InsightsBox;
