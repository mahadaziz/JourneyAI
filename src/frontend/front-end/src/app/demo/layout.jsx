import React from 'react';
import '../globals.css';

export const metadata = {
  title: 'City fuel consumption | JourneyAI demo',
  description: 'Explore six model years of synthetic vehicle data and a sample reporting hypothesis.',
};

export default function DemoLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
