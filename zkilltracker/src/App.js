import './App.css';
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import CorporationView from './components/corporationView';


function App() {
  return (
    <Routes>
      <Route path="/" element={<CorporationView />} />
    </Routes>
  );
}

export default App;
