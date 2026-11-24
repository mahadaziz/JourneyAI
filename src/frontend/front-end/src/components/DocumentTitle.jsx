'use client';

import React, { useContext } from 'react';
import { EditorDataContext } from '../context/EditorDataContext';

function DocumentTitle() {
  const { title, setTitle } = useContext(EditorDataContext);
  return (
    <div className="documentTitle hidden md:flex md:pl-4 lg:pl-4 xl:pl-24 text-white">
      <input
        type="text"
        aria-label="Draft title"
        placeholder="Untitled document"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />
    </div>
  );
}

export default DocumentTitle;
