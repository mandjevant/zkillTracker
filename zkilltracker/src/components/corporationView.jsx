import React, { useState, useEffect } from 'react';
import ChooseCorpDisplay from './chooseCorpDropdown';
import Menu from './menu';

export default function CorporationView() {
  const [activeCorporationId, setActiveCorporationId] = useState(98753041);
  const [activeCorporation, setActiveCorporation] = useState(false);

  useEffect(() => {
    fetch("/corporation/" + String(activeCorporationId)).then(res => res.json()).then(data => {
      setActiveCorporation(data);
    });
  }, [activeCorporationId]);

  return (
    <div className="App">
        <Menu />
        <ChooseCorpDisplay activeCorporation={activeCorporation} setActiveCorporationId={setActiveCorporationId} />
    </div>
  );
}