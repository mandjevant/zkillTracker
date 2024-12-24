import './App.css';
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import CorporationView from './components/corporationView';
import AllianceView from './components/allianceView';
import MemberView from './components/memberView';
import AdminView from './components/adminView';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';


function App() {
  return (
    <MantineProvider defaultColorScheme="dark">
      <Notifications limit={5} zIndex={1000} />
      <Routes>
        <Route path="/" element={<CorporationView />} />
        <Route path="/alliance" element={<AllianceView />} />
        <Route path="/members" element={<MemberView />} />
        <Route path="/admin" element={<AdminView />} />
      </Routes>
    </MantineProvider>
  );
}

export default App;
