'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import 'react-quill/dist/quill.snow.css';
// import 'react-quill/dist/quill.bubble.css';
import '../app/globals.css'
// React Quill??

const ReactQuill = dynamic(
    () => import('react-quill'),
    {
      ssr: false, // This line is important. It's what prevents server-side render
      loading: () => <p>Loading...</p>, // Optional loading component
    }
  );
  
  // // Define the toolbar options
  // const modules = {
  //   toolbar: {
  //     container: "#toolbar", // This should match the ID of your custom toolbar
  //   },
  // };

  const formats = [
    'bold',
    'italic',
    'underline',
    'header', // You can specify header values as needed
    'list',
    'bullet',
    'link',
    'clean', // This format is for removing formatting
  ];


const TextBox = () => {
  const [value, setValue] = useState('');
  const quillRef = useRef(null); // Ref to get the Quill instance

  return (
    <div className="flex flex-col row-span-3 col-span-2 pl-3 pb-3">
      {/* Quill Editor */}
      <ReactQuill
        ref={quillRef}
        theme="snow"
        value={value}
        onChange={setValue}
        modules={{
          toolbar: '#toolbar', // Selector for the custom toolbar
        }}
        formats={formats}
      />
      {/* You can place your custom toolbar here if you prefer it at the bottom */}

      {/* Custom Toolbar */}
      <div id="toolbar">
        {/* Bold, Italic, and Underline buttons */}
        <button className="ql-bold" title="Bold"></button>
        <button className="ql-italic" title="Italic"></button>
        <button className="ql-underline" title="Underline"></button>

        <button className="ql-header" value="1" title="Heading 1">H1</button>
        <button className="ql-header" value="2" title="Heading 2">H2</button>

        {/* Lists */}
        <button className="ql-list" value="ordered" title="Ordered List"></button>
        <button className="ql-list" value="bullet" title="Bullet List"></button>

        {/* Link */}
        <button className="ql-link" title="Insert Link"></button>

        {/* Clear formatting */}
        <button className="ql-clean" title="Clear Formatting"></button>
      </div>
    </div>
  );
};

export default TextBox;