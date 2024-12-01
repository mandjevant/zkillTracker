import './App.css';
import React, { useState, useEffect } from 'react';

function App() {
  const [activeCorporation, setActiveCorporation] = useState(98753041);
  const [corporationInfo, setCorporationInfo] = useState(0);

  useEffect(() => {
      fetch("/corporation/" + String(activeCorporation)).then(res => res.json()).then(data => {
        setCorporationInfo(data.name);
      })
    }
  )

  return (
    <div className="App">
      <p>{corporationInfo}</p>
    </div>
  );
}

export default App;
