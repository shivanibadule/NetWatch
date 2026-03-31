import React from 'react';
import Dashboard from './pages/Dashboard';
import { ThemeProvider } from './context/ThemeContext';
import ChatWindow from './components/ChatWindow';

export default function App() {
  return (
    <ThemeProvider>
      <Dashboard />
      <ChatWindow />
    </ThemeProvider>
  );
}
