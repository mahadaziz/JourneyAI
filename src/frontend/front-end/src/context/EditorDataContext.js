'use client';

import React, { useEffect, useState } from 'react';

export const EditorDataContext = React.createContext({});

export function EditorDataProvider({
  children, datasetId, initialTitle, revision,
}) {
  const [title, setTitle] = useState(initialTitle);
  const [contextText, setContextText] = useState('');

  useEffect(() => {
    if (revision === 0) {
      const previousTitle = localStorage.getItem(`journeyai:title:${datasetId}`);
      if (previousTitle?.trim()) setTitle(previousTitle);
    }
  }, [datasetId, revision]);

  return (
    <EditorDataContext.Provider value={{
      title, setTitle, contextText, setContextText,
    }}
    >
      {children}
    </EditorDataContext.Provider>
  );
}
