"use client"
import { UserCircleIcon } from '@heroicons/react/24/solid';
import React, { useState } from 'react';
export default function Page() {
  const [isHidden, setIsHidden] = useState(true);

  const toggleVisibility = () => {
    setIsHidden(!isHidden);
  };
  
  return (
    <section className='min-h-screen flex flex-col justify-between bg-bgGrey text-black'>
      
      {/* Search bar and User Menu at the top */}
      <div className="flex w-full justify-center items-center relative p-12">
        <div className="flex-grow flex justify-center">
          <input
            type="text"
            placeholder="Search for a dataset..."
            className="bg-gray-200 text-gray-800 p-2 rounded-md"
          />
        </div>
        <div className="relative">
          <button onClick={toggleVisibility} type="button" className="flex  mr-3 text-sm bg-gray-200 rounded-full md:mr-0 focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600" id="user-menu-button" aria-expanded="false" data-dropdown-toggle="user-dropdown" data-dropdown-placement="bottom">
            <span className="sr-only">Open user menu</span>
            <UserCircleIcon className='w-10 h-10 rounded-full bg-white'/>
            {/* <img className="w-8 h-8 rounded-full" src="/docs/images/people/profile-picture-3.jpg" alt="user photo"/> */}
          </button>
          <div className={`right-0 ${isHidden ? 'hidden' : ''} absolute z-50 my-4 text-base list-none bg-white divide-y divide-gray-100 rounded-lg shadow dark:bg-gray-700 dark:divide-gray-600`} id="user-dropdown">
            <div className="px-4 py-3">
              <span className="block text-sm text-gray-900 dark:text-white">User 1</span>
              <span className="block text-sm  text-gray-500 truncate dark:text-gray-400">user1@journey.com</span>
            </div>
            <ul className="py-2" aria-labelledby="user-menu-button">
              <li>
                <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Dashboard</a>
              </li>
              <li>
                <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Settings</a>
              </li>
              <li>
                <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Sign out</a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Dataset cards in the middle */}
      <div className="flex justify-center items-center grid grid-cols-4 bg-bgGrey text-center max-w-screen-md mx-auto">
        {/* First Row */}
        <div className="h-48 w-36 bg-white rounded-lg shadow-lg shadow-bottom py-4 mx-5 mb-6">
          <p className="text-lg">Upload Dataset</p>
        </div>

        <div className="h-48 w-36 bg-white rounded-lg shadow-lg shadow-bottom py-4 mx-5 mb-6">
          <p className="text-lg">Fuel Consumption</p>
        </div>
      </div>

      {/* Copyright message at the bottom */}
      <div className="relative bottom-0 left-0 right-0 p-4 text-center bg-bgGrey">
        2023 Journey AI, All rights reserved
      </div>
    </section>
  );
}
