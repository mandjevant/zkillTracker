import React, { useState, useEffect } from 'react'
import axios from 'axios';

export default function ChooseCorpDropdown( { activeCorporation, setActiveCorporationId }) {
  const [allCorporations, setAllCorporations] = useState([]);
  const [open, setOpen] = useState(false);
  const [dropdownText, setDropdownText] = useState("Select a corporation")

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
    setActiveCorporationId(corpID);
    setOpen(!open);
  }

  useEffect(() => {
    if (!activeCorporation) {
      return
    } else {
      setDropdownText(activeCorporation.name);
    }
  }, [activeCorporation])

  return (
    <div className="dropdownContainer">
      <div className="dropdownButton" onClick={() => setOpen(!open)}>
        {dropdownText}
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