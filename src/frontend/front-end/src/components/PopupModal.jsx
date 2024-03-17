'use client';

import React, { useState, useEffect } from 'react';
import ScatterPlot from './ScatterPlot';
import BarGraph from './BarGraph';
import LineGraph from './LineGraph';

function PopupModal({ isModalOpen, closeModal, array }) {
  const [visibility, setVisibility] = useState('hidden');

  useEffect(() => {
    let timeoutId;

    if (!isModalOpen) {
      timeoutId = setTimeout(() => {
        setVisibility('hidden');
      }, 300);
    } else {
      setVisibility('visible');
    }
    return () => clearTimeout(timeoutId);
  }, [isModalOpen]);

  const modalBackgroundStyle = isModalOpen
    ? {
      visibility,
      opacity: 1,
      transform: 'scale(1)',
      transition: 'opacity 0.3s ease, transform 0.3s ease',
    }
    : {
      visibility,
      opacity: 0,
      transform: 'scale(0.95)',
      transition: 'opacity 0.3s ease, transform 0.3s ease',
      pointerEvents: 'none',
    };

  const handleModalClick = (e) => {
    e.stopPropagation();
  };

  const getAdditionalProps = () => {
    if (array.length > 0 && array[0] == 'scatter') {
      return {
        xField: array[1],
        yField: array[2]
      };
    }
    else if (array.length > 0) {
      return {
        xField: array[1],
        yField: array[2],
        title: array[3]
      };
    }
    return {};
  };

  const renderChart = () => {
    const chartType = array.length > 0 ? array[0] : null;
  
    switch (chartType) {
      case 'line':
        return <LineGraph chartData={array} {...getAdditionalProps()} />;
      case 'bar':
        return <BarGraph chartData={array} {...getAdditionalProps()} />;
      case 'scatter':
        return <ScatterPlot chartData={array} {...getAdditionalProps()} />;
      default:
        return <div>Loading chart data...</div>;
    }
  }
  

  return (
    <div
      role="button"
      id="popup-modal"
      tabIndex="-1"
      onClick={closeModal}
      style={modalBackgroundStyle}
      className="overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 bottom-0 z-50 flex justify-center items-center w-screen h-screen"
    >
      <div
        role="button"
        id="modalClick"
        tabIndex={0}
        className="relative p-4 w-max h-max max-w-[90vw] max-h-[90vh]"
        onClick={handleModalClick}
      >
        <div className="relative flex justify-center items-center bg-white rounded-lg shadow dark:bg-gray-700">
          <div className="flex justify-center items-center overflow-auto p-4 md:p-5">
            <div>
              {array ? renderChart() : <div>Loading chart data...</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PopupModal;
