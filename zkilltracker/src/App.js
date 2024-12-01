import './App.css';
import React, { useState, useEffect } from 'react';
import ChooseCorpDropdown from './components/chooseCorpDropdown';

function App() {
  const [activeCorporationId, setActiveCorporationId] = useState(98753041);
  const [activeCorporation, setActiveCorporation] = useState(false);

  useEffect(() => {
    fetch("/corporation/" + String(activeCorporationId)).then(res => res.json()).then(data => {
      setActiveCorporation(data);
    });
  }, [activeCorporationId]);

  return (
    <div className="App">
      <p>{activeCorporation.name}</p>
      <ChooseCorpDropdown activeCorporation={activeCorporation} setActiveCorporationId={setActiveCorporationId} />
    </div>
  );
}

export default App;
