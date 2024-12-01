import './App.css';
import React, { useState, useEffect } from 'react';
import ChooseCorpDropdown from './components/chooseCorpDropdown';

function App() {
  const [activeCorporation, setActiveCorporation] = useState(98753041);
  const [corporationInfo, setCorporationInfo] = useState(0);

  useEffect(() => {
    fetch("/corporation/" + String(activeCorporation)).then(res => res.json()).then(data => {
      setCorporationInfo(data.name);
    });
  }, [activeCorporation]);

  return (
    <div className="App">
      <p>{corporationInfo}</p>
      <ChooseCorpDropdown setActiveCorporation={setActiveCorporation} />
    </div>
  );
}

export default App;
