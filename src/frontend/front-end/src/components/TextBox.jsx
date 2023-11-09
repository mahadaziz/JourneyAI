'use client';

import React, { useState, useEffect } from 'react';
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
  
  const TextBox = () => {
    const [value, setValue] = useState('');

    const handleChange = (content, delta, source, editor) => {
      setValue(editor.getHTML()); // Or directly content
    };

    // Implement undo and redo functions
    const undoChange = () => {
      const editor = quillRef.current.getEditor();
      editor.history.undo();
    };

    const redoChange = () => {
      const editor = quillRef.current.getEditor();
      editor.history.redo();
    };

// Define the toolbar options
const modules = {
  toolbar: [
    ['bold', 'italic', 'underline', 'strike'], // toggled buttons
    ['blockquote', 'code-block'],

    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    [{ 'script': 'sub'}, { 'script': 'super' }], // superscript/subscript
    [{ 'indent': '-1'}, { 'indent': '+1' }], // outdent/indent
    [{ 'direction': 'rtl' }], // text direction

    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],

    [{ 'color': [] }, { 'background': [] }], // dropdown with defaults from theme
    [{ 'font': [] }],
    [{ 'align': [] }],

    ['clean'], // remove formatting button

    ['undo', 'redo'], // Add undo and redo functions
  ],
};
    return (
      <div className='row-span-3 col-span-2 pl-3 pb-3'>
      {/* ReactQuill component */}
      <div className="flex-grow">
        <ReactQuill
          theme="snow"
          value={value}
          onChange={handleChange}
          modules={modules}
        />
      </div>
    </div>
    );
  };

export default TextBox;