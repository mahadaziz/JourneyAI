'use client';

import React, { useState, useContext } from 'react';
import { useRouter } from 'next/navigation';
import { UploadIcon } from './Icons';
import '../app/globals.css';

function UploadForm({
  isVisible, toggleVisibility, userId,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [title, setTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const router = useRouter();

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Handle the file (upload to server, read contents, etc.)
      setSelectedFile(file);
      console.log('File selected:', file.name);
    }
  };

  const handleTitleChange = (event) => {
    setTitle(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      console.log('No file selected');
      return;
    }
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('user_id', userId);
    formData.append('title', title);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_LOCAL_URL}/upload_dataset`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log('File uploaded successfully', data);
        localStorage.setItem('dataSetInfo', JSON.stringify(data)); // Store the data in localStorage
        toggleVisibility(false);
        router.push('/dashboard');
      } else {
        console.error('Upload failed with status:', response.status);
      }
    } catch (error) {
      console.error('Error making the API call:', error.message);
    }
  };

  return (
    <div id="authentication-modal" aria-hidden="true" className={`${isVisible ? '' : 'hidden'} overflow-y-auto overflow-x-hidden flex z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full`}>
      <div className="p-4 w-full max-w-md max-h-full">

        <div className="relative bg-white rounded-lg shadow dark:bg-gray-700">
          <div className="flex items-center justify-between p-4 md:p-5 border-b rounded-t dark:border-gray-600">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
              Upload Dataset
            </h3>
            <button type="button" onClick={() => toggleVisibility(false)} className=" text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white" data-modal-hide="authentication-modal">
              <svg className="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6" />
              </svg>
              <span className="sr-only">Close modal</span>
            </button>
          </div>
          <div className="p-4 md:p-5">
            <form className="space-y-4 " action="#">
              <div>
                <label className="block mb-2 text-md font-medium text-gray-900 dark:text-white">Enter your Title:</label>
                <input
                  type="text"
                  name="title"
                  id="title"
                  className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"
                  placeholder="Enter document title"
                  required
                  onChange={handleTitleChange}
                />
              </div>
              <div className="flex flex-col">
                <label className="text-md font-medium text-gray-900">Upload your dataset:</label>
                <div className="flex justify-center items-center p-5">
                  <label className="rounded hover:text-gray-500 cursor-pointer">
                    <UploadIcon />
                    <input
                      type="file"
                      accept=".csv"
                      style={{ display: 'none' }}
                      onChange={handleFileUpload}
                    />
                  </label>
                </div>
                <div className="flex justify-center items-center">
                  {selectedFile?.name}
                </div>
              </div>
              <div className="flex justify-center">
                {isLoading ? (
                  <div className="flex justify-center items-center pt-12" role="status">
                    <svg aria-hidden="true" className="inline w-8 h-8 text-black animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                      <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
                    </svg>
                    <span className="sr-only">Loading...</span>
                  </div>
                ) : (
                  <button type="button" onClick={handleSubmit}>
                    Submit
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadForm;
