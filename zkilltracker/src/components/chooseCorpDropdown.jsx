import React, { useState, useEffect } from 'react'
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function ChooseCorpDropdown( { activeCorporation, setActiveCorporationId }) {
  const [allCorporations, setAllCorporations] = useState([]);
  const [open, setOpen] = useState(false);
  const [displayOptionsOpen, setDisplayOptionsOpen] = useState(false);
  const [dropdownText, setDropdownText] = useState("Select a corporation")
  const [monthsData, setMonthsData] = useState("")
  const corpDisplayOptions = ["Ships", "Points", "Isk"]
  const [displayOptionsDropdownText, setDisplayOptionsDropdownText] = useState("Ships")

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

  function handleDisplayDropdownChoice(name) {
    setDisplayOptionsDropdownText(name);
    setDisplayOptionsOpen(!displayOptionsOpen);
  }

  useEffect(() => {
    if (!activeCorporation) {
      return
    } else {
      setDropdownText(activeCorporation.name);
    }
  }, [activeCorporation])

  useEffect(() => {
    axios.get("/corporation/"+String(activeCorporation.id)+"/months")
      .then(res => {
        setMonthsData(res.data);
      })
      .catch(error => {
        console.error("Error fetching corporations: ", error);
      })
  }, [activeCorporation])
 
  return (
    <div>
      <div className="corporationChooser">
        <p>Corporation</p>
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
      </div>
      <div className="viewMonths">
        <ResponsiveContainer width={"100%"} height={"100%"}>
          <LineChart data={monthsData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <XAxis xAxisId={1} interval={10} dataKey="year" tick={{fontSize: 18, angle: 0}} />
            <YAxis />
            <Tooltip contentStyle={{backgroundColor: "#1e1e1e", borderRadius: "8px"}} />
            <Legend wrapperStyle={{bottom: -2}} />
            <Line
              type="monotone"
              dataKey={`${displayOptionsDropdownText.toLowerCase()}Destroyed`}
              stroke="#82ca9d"
              activeDot={{ r: 8 }}
            />
            <Line 
              type="monotone" 
              dataKey={`${displayOptionsDropdownText.toLowerCase()}Lost`} 
              stroke="#b64949" 
            />
          </LineChart>
        </ResponsiveContainer>
        <div className="corporationGraphSelectors">
            <div className="dropdownContainer">
              <div className="dropdownButton" onClick={() => setDisplayOptionsOpen(!displayOptionsOpen)}>
                {displayOptionsDropdownText}
              </div>
              <div className="dropdownContent" style={{display: displayOptionsOpen ? 'flex' : 'none'}}>
                {corpDisplayOptions.map((displayOption, index) => (
                  <div className="dropdownItem" key={index} onClick={() => handleDisplayDropdownChoice(displayOption)}>
                    {displayOption}
                  </div>
                ))}
              </div>
            </div>
        </div>
      </div>
    </div>
  )
}