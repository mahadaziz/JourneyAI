'use client';

import React, { useState, useEffect } from 'react';

export const EditorDataContext = React.createContext({
  editorText: '',
  setEditorText: () => {},
  contextText: '',
  setContextText: () => {},
});

export function EditorDataProvider({ children }) {
  const [editorText, setEditorText] = useState('');
  const [contextText, setContextText] = useState('');

  return (
    <EditorDataContext.Provider value={{
      editorText, setEditorText, contextText, setContextText,
    }}
    >
      {children}
    </EditorDataContext.Provider>
  );
}
