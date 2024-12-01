import React, { useState, useEffect } from 'react'
import axios from 'axios';

export default function ChooseCorpDropdown( { setActiveCorporation }) {
  const [allCorporations, setAllCorporations] = useState([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    axios.get("/corporations")
      .then(res => {
        setAllCorporations(res.data);
      })
      .catch(error => {
        console.error("Error fetching corporations: ", error);
      });
  }, []);

  function handleDropdownChoice(corpID) {
    setActiveCorporation(corpID)
  }

  return (
    <div className="dropdownContainer">
      <div className="dropdownButton" onClick={() => setOpen(!open)}>
        Select a corporation
      </div>
      <div className="dropdownContent" style={{display: open ? 'flex' : 'none'}}>
        {allCorporations.map((corp, index) => (
          <div className="dropdownItem" key={index} onClick={() => handleDropdownChoice(corp.id)}>
            {corp.name}
          </div>
        ))}
      </div>
    </div>
  )
}