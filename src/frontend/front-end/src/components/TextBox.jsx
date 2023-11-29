'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'react-quill/dist/quill.snow.css';
import '../app/globals.css'
import EditorPlaceholder from './EditorPlaceholder';
import { Tooltip } from 'react-tooltip'



const ReactQuill = dynamic(
    () => import('react-quill'),
    {
      ssr: false, // This line is important. It's what prevents server-side render
      // loading: () => <p className='text-black'>Loading...</p>, // Optional loading component
      loading: () => <EditorPlaceholder/>
    }
  );
  
  const TextBox = () => {
    const [value, setValue] = useState('');
    const [wordCount, setWordCount] = useState(0);
    const quillRef = React.useRef();

    // Function to count words
    const countWords = (text) => {
      return text.split(/\s+/).filter(Boolean).length;
    };

    // Handle the text change
    const handleTextChange = (content, delta, source, editor) => {
      setValue(content);
      setWordCount(countWords(editor.getText()));
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
    const formats = [
      'bold',
      'italic',
      'underline',
      'header', 
      'list',
      'bullet',
      'link',
      'clean', // This format is for removing formatting
    
    ];

  return (
    <div className="row-span-3 col-span-2 pl-5 delayAnimation">
      {/* Quill Editor */}
      <ReactQuill className="delayAnimation"
        theme="snow"
        value={value}
        onChange={handleTextChange}
        modules={{
          toolbar: '#toolbar', // Selector for the custom toolbar
        }}
        formats={formats}
        placeholder="Start typing..."

      />
      {/* Custom Toolbar */}
      <div id="toolbar" className="delayAnimation">
      <Tooltip id="my-tooltip" />
        {/* Bold, Italic, and Underline buttons */}
        <div className='toolbar-group border-r-2'>
          <button className="ql-bold" data-tooltip-id="my-tooltip" data-tooltip-content="Bold" data-tooltip-place="top" title="Bold"></button>
          <button className="ql-italic" data-tooltip-id="my-tooltip" data-tooltip-content="Italic" data-tooltip-place="top" title="Italic"></button>
          <button className="ql-underline" data-tooltip-id="my-tooltip" data-tooltip-content="Underline" data-tooltip-place="top" title="Underline"></button>
        </div>

        <div className='toolbar-group border-r-2'>
          <button className="ql-header" data-tooltip-id="my-tooltip" data-tooltip-content="Header 1" data-tooltip-place="top" value="1" title="Heading 1">H1</button>
          <button className="ql-header" data-tooltip-id="my-tooltip" data-tooltip-content="Header 2" data-tooltip-place="top" value="2" title="Heading 2">H2</button>
        </div>

        {/* Lists */}
        <div className='toolbar-group border-r-2'>
          <button className="ql-list" data-tooltip-id="my-tooltip" data-tooltip-content="Ordered List" data-tooltip-place="top" value="ordered" title="Ordered List"></button>
          <button className="ql-list" data-tooltip-id="my-tooltip" data-tooltip-content="Bullet List" data-tooltip-place="top" value="bullet" title="Bullet List"></button>
        </div>

        {/* Link */}
        <div className='toolbar-group'>
          <button className="ql-link" data-tooltip-id="my-tooltip" data-tooltip-content="Link" data-tooltip-place="top" title="Insert Link"></button>
        </div>

        <div className='toolbar-group'>
          {/* Clear formatting */}
          <button className="ql-clean" data-tooltip-id="my-tooltip" data-tooltip-content="Remove Format" data-tooltip-place="top" title="Clear Formatting"></button>
        </div>

        {/* Word Count */}
        <div className="ml-12 mr-5 text-gray-400 dark:text-white">{wordCount} words</div>
      </div>
    </div>
  );
};

export default TextBox;