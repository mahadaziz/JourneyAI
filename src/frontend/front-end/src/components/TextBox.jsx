'use client';
import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import 'react-quill/dist/quill.snow.css';
import '../app/globals.css'

const ReactQuill = dynamic(
    () => import('react-quill'),
    {
      ssr: false, // This line is important. It's what prevents server-side render
      loading: () => <p>Loading...</p>, // Optional loading component
    }
  );
  
  const TextBox = () => {
    const [value, setValue] = useState('');
    const quillRef = useRef(null); // Ref to get the Quill instance

    // Implement undo and redo functions
    const undoChange = () => {
      const editor = quillRef.current.getEditor();
      editor.history.undo();
    };

    const redoChange = () => {
      const editor = quillRef.current.getEditor();
      editor.history.redo();
    };

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

  return (
    <div className="row-span-3 col-span-2 pl-3 pr-3">
      {/* Quill Editor */}
      <ReactQuill className=''
        ref={quillRef}
        theme="snow"
        value={value}
        onChange={setValue}
        modules={{
          toolbar: '#toolbar', // Selector for the custom toolbar
        }}
        formats={formats}
        placeholder="Start typing..." // Add your placeholder text here

      />
      {/* Custom Toolbar */}
      <div id="toolbar">
        {/* Bold, Italic, and Underline buttons */}
        <div className='toolbar-group border-r-2'>
          <button className="ql-bold" title="Bold"></button>
          <button className="ql-italic" title="Italic"></button>
          <button className="ql-underline" title="Underline"></button>
        </div>

        <div className='toolbar-group border-r-2'>
          <button className="ql-header" value="1" title="Heading 1">H1</button>
          <button className="ql-header" value="2" title="Heading 2">H2</button>
        </div>

        {/* Lists */}
        <div className='toolbar-group border-r-2'>
          <button className="ql-list" value="ordered" title="Ordered List"></button>
          <button className="ql-list" value="bullet" title="Bullet List"></button>
        </div>

        {/* Link */}
        <div className='toolbar-group border-r-2'>
          <button button className="ql-link" title="Insert Link"></button>
        </div>

        <div className='toolbar-group border-r-2'>
          {/* Clear formatting */}
          <button className="ql-clean" title="Clear Formatting"></button>
        </div>

      </div>
    </div>
  );
};

export default TextBox;