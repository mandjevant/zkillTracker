import React, { useState, useEffect } from 'react';
import Menu from './menu';
import axios from 'axios';
import { Select, Table } from '@mantine/core';
import { LineChart } from "@mantine/charts";
import { showNotification } from '@mantine/notifications';
import { negaNotifProps } from './helpers';

export default function CorporationView() {
  const [activeCorporationId, setActiveCorporationId] = useState(98753041);
  const [allCorporations, setAllCorporations] = useState([]);
  const [monthsData, setMonthsData] = useState("")
  const corpDisplayOptions = ["Ships", "Points", "Isk"]
  const [displayOptionsDropdownText, setDisplayOptionsDropdownText] = useState("Ships")
  const [corpMonthKillRows, setCorpMonthKillRows] = useState([])

  // useEffect(() => {
  //   fetch(`/corporation/${activeCorporationId.toString()}`)
  //     .then(res => {
  //       setActiveCorporation(res.data);
  //     })
  //     .catch(error => {
  //       showNotification({
  //         message: "Error fetching corporation",
  //         ...negaNotifProps
  //       })
  //       console.error("Error fetching corporations: ", error);
  //     });
  // }, [activeCorporationId]);
  
  useEffect(() => {
    axios.get("/corporations")
      .then(res => {
        setAllCorporations(res.data);
      })
      .catch(error => {
        showNotification({
          message: "Error fetching corporations",
          ...negaNotifProps
        })
        console.error("Error fetching corporations: ", error);
      });
  }, []);

  useEffect(() => {
    if (!activeCorporationId) {
      return
    }
    axios.get(`/corporation/${activeCorporationId.toString()}/months`)
      .then(res => {
        const corporationsWithMonthYearConcat = res.data.map(corp => {
          return {
            ...corp,
            monthYearConcat: `${corp.year}-${corp.month}`
          };
        });
        setMonthsData(corporationsWithMonthYearConcat);
      })
      .catch(error => {
        showNotification({
          message: "Error fetching corporation",
          ...negaNotifProps
        })
        console.error("Error fetching corporation: ", error);
      })
  }, [activeCorporationId])

  useEffect(() => {
    if (!activeCorporationId) {
      return
    }

    setCorpMonthKillRows([]);
    const curYear = new Date().getFullYear()
    const curMonth = new Date().getMonth()

    axios.get(`/corporation/${activeCorporationId.toString()}/kills/year/${curYear}/month/${curMonth+1}`)
      .then(res => {
        const rows = res.data.map((kill, index) => (
          <Table.Tr key={index}>
            <Table.Td>{kill.characterName}</Table.Td>
            <Table.Td style={{textAlign: 'right'}}>{kill.kills}</Table.Td>
          </Table.Tr>
        ))
        setCorpMonthKillRows(rows)
      }).catch(error => {
        showNotification({
          message: "Error fetching kills",
          ...negaNotifProps
        })
        console.error("Error fetching kills: ", error);
      })
  }, [activeCorporationId])


  return (
    <div className="App">
      <Menu />
      <div>
        <div className="corporationChooser">
          <Select
            checkIconPosition="right"
            label="Choose corporation"
            placeholder="Mostly Cap Stable"
            data={allCorporations.map((corp) => ({value: corp.id.toString(), label: corp.name}))}
            searchable
            defaultValue={["Mostly Cap Stable"]}
            onChange={setActiveCorporationId}
            allowDeselect={false}
          />
        </div>
        <div className="viewGraph">
          <LineChart
            data={monthsData}
            dataKey={"monthYearConcat"}
            series={[
              { name: `${displayOptionsDropdownText.toLowerCase()}Destroyed`, color: '#82ca9d' },
              { name: `${displayOptionsDropdownText.toLowerCase()}Lost`, color: '#b64949' },
            ]}
            curveType="natural"
            withLegend
            tooltipAnimationDuration={100}
            xAxisLabel={"Year-Month"}
            yAxisLabel={"Amount"}
          />
          <div className="corporationGraphSelectors">
            <Select 
              checkIconPosition="right"
              label="Choose statistic"
              placeholder="Ships"
              data={corpDisplayOptions}
              searchable
              defaultValue={["Ships"]}
              onChange={setDisplayOptionsDropdownText}
              allowDeselect={false}
            />
            <h5 className="tableTitle">
              Top killers this month
            </h5>
            <Table.ScrollContainer minWidth={"13vw"} className="corpTable">
              <Table horizontalSpacing="md">
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Character</Table.Th>
                    <Table.Th style={{textAlign: 'right'}}>Kills</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>{corpMonthKillRows}</Table.Tbody>
              </Table>
            </Table.ScrollContainer>
          </div>
        </div>
      </div>
    </div>
  );
}