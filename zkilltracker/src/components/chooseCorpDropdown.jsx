import React, { useState, useEffect } from 'react'
import axios from 'axios';
import { LineChart } from "@mantine/charts";

export default function ChooseCorpDisplay( { activeCorporation, setActiveCorporationId }) {
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
    if (!activeCorporation) {
      return
    }
    axios.get("/corporation/"+String(activeCorporation.id)+"/months")
      .then(res => {
        const corporationsWithMonthYearConcat = res.data.map(corp => {
          return {
            ...corp,
            monthYearConcat: `${corp.month}-${corp.year}`
          };
        });
        setMonthsData(corporationsWithMonthYearConcat);
      })
      .catch(error => {
        console.error("Error fetching corporation: ", error);
      })
  }, [activeCorporation])
 
  return (
    <div>
      <div className="corporationChooser">
        <p>Corporation:</p>
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
      <div className="viewGraph">
        <LineChart
          data={monthsData}
          dataKey={"monthYearConcat"}
          series={[
            { name: `${displayOptionsDropdownText.toLowerCase()}Destroyed`, color: '#82ca9d'},
            { name: `${displayOptionsDropdownText.toLowerCase()}Lost`, color: '#b64949'},
          ]}
          curveType="natural"
          withLegend
          tooltipAnimationDuration={100}
          xAxisLabel={"Month-Year"}
          yAxisLabel={"Amount"}
        />
        <div className="corporationGraphSelectors">
            <p>Display:</p>
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