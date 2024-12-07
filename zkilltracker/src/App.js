import './App.css';
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import CorporationView from './components/corporationView';
import { MantineProvider } from '@mantine/core';
import AllianceView from './components/allianceView';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';


function App() {
  return (
    <MantineProvider defaultColorScheme="dark">
      <Routes>
        <Route path="/" element={<CorporationView />} />
        <Route path="/alliance" element={<AllianceView />} />
      </Routes>
    </MantineProvider>
  );
}

export default App;
