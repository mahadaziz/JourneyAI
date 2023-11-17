'use client';
import React, { useState } from 'react';


const OptionsMenu = () => {
    // State to keep track of whether the dropdown is open
    const [isOpen, setIsOpen] = useState(false);

    // Function to toggle the dropdown state
    const toggleDropdown = () => setIsOpen(!isOpen);

    return (
        <div className="relative">
            <button onClick={toggleDropdown} 
                id="dropdownDefaultButton" 
                data-dropdown-toggle="dropdown" className="relative focus:outline-none 
                font-medium rounded-2xl text-sm px-5 py-2.5 border border-gray-700 text-center inline-flex items-center
                w-auto min-w-0 sm:min-w-[300px] md:min-w-[400px] lg:min-w-[500px]
                text-black bg-white hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200" 
                
                type="button">
                Tell me about...
                <svg className="w-2.5 h-2.5 ms-auto" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 4 4 4-4"/>
                </svg>
            </button>
            <div className={`z-10 ${isOpen ? '' : 'hidden'} absolute bg-white divide-y divide-gray-100 rounded-2xl shadow w-full dark:bg-gray-700`}>
                <ul className="py-2 text-sm text-gray-700 dark:text-gray-200" aria-labelledby="dropdownDefaultButton">
                <li>
                    <a href="#" className="block px-4 py-2 hover:bg-gray-300 dark:hover:bg-gray-600 dark:hover:text-white">Emissions</a>
                </li>
                <li>
                    <a href="#" className="block px-4 py-2 hover:bg-gray-300 dark:hover:bg-gray-600 dark:hover:text-white">Idk1</a>
                </li>
                <li>
                    <a href="#" className="block px-4 py-2 hover:bg-gray-300 dark:hover:bg-gray-600 dark:hover:text-white">Idk2</a>
                </li>
                </ul>
            </div>
        </div>
    );

}

export default OptionsMenu;