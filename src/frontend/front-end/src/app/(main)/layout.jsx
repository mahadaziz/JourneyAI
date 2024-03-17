import React from 'react';
import '../globals.css';
import { EditorDataProvider } from '../../context/EditorDataContext';

export const metadata = {
  title: 'Data Driven Stories',
  description: '',
};

export default function RootLayout({ children }) {
  return (
    <EditorDataProvider>
      {children}
    </EditorDataProvider>

  );
}
