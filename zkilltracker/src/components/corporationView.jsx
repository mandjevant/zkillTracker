import React, { useState, useEffect } from 'react';
import Menu from './menu';
import axios from 'axios';
import { Select, Table, Tabs, Tooltip } from '@mantine/core';
import { LineChart } from "@mantine/charts";
import { showNotification } from '@mantine/notifications';
import { negaNotifProps } from './helpers';
import { IconListTree, IconCalendarMonth } from '@tabler/icons-react';

export default function CorporationView() {
  const [activeCorporationId, setActiveCorporationId] = useState(98753041);
  const [allCorporations, setAllCorporations] = useState([]);
  const [monthsData, setMonthsData] = useState("");
  const corpDisplayOptions = ["Ships", "Points", "Isk"];
  const [displayOptionsDropdownText, setDisplayOptionsDropdownText] = useState("Ships");
  const [corpMonthKillRows, setCorpMonthKillRows] = useState([]);
  const [corpLastMonthKillRows, setCorpLastMonthKillRows] = useState([]);
  const [corpLastMonthLowKillRows, setCorpLastMonthLowKillRows] = useState([]);
  const [corpDeadbeatsRows, setCorpDeadbeatsRows] = useState([]);

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
    const curYear = new Date().getFullYear();
    const curMonth = new Date().getMonth();

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
          message: "Error fetching this month's kills",
          ...negaNotifProps
        })
        console.error("Error fetching this month's kills: ", error);
      })
  }, [activeCorporationId])


  useEffect(() => {
    if (!activeCorporationId) {
      return
    }
    
    setCorpLastMonthKillRows([]);
    const curYear = new Date().getFullYear();
    const curMonth = new Date().getMonth();

    let prevMonth, prevYear;
    if (curMonth === 0) {
      prevMonth = 11;
      prevYear = curYear-1;
    } else {
      prevMonth = curMonth-1;
      prevYear = curYear;
    }
    
    axios.get(`/corporation/${activeCorporationId.toString()}/kills/year/${prevYear}/month/${prevMonth+1}`)
      .then(res => {
        const rows = res.data.map((kill, index) => (
          <Table.Tr key={index}>
            <Table.Td>{kill.characterName}</Table.Td>
            <Table.Td style={{textAlign: 'right'}}>{kill.kills}</Table.Td>
          </Table.Tr>
        ))
        setCorpLastMonthKillRows(rows)
      }).catch(error => {
        showNotification({
          message: "Error fetching last month's kills",
          ...negaNotifProps
        })
        console.error("Error fetching last month's kills: ", error);
      })
  }, [activeCorporationId])

  useEffect(() => {
    if (!activeCorporationId) {
      return
    }
    
    setCorpLastMonthLowKillRows([]);
    const curYear = new Date().getFullYear();
    const curMonth = new Date().getMonth();

    let prevMonth, prevYear;
    if (curMonth === 0) {
      prevMonth = 11;
      prevYear = curYear-1;
    } else {
      prevMonth = curMonth-1;
      prevYear = curYear;
    }

    axios.get(`/corporation/${activeCorporationId.toString()}/low_kills/year/${prevYear}/month/${prevMonth+1}`)
      .then(res => {
        const rows = res.data.map((kill, index) => (
          <Table.Tr key={index}>
            <Table.Td>{kill.characterName}</Table.Td>
            <Table.Td style={{textAlign: 'right'}}>{kill.kills}</Table.Td>
          </Table.Tr>
        ))
        setCorpLastMonthLowKillRows(rows)
      }).catch(error => {
        showNotification({
          message: "Error fetching last month's low kills",
          ...negaNotifProps
        })
        console.error("Error fetching last month's low kills: ", error);
      })
  }, [activeCorporationId])

  useEffect(() => {
    if (!activeCorporationId) {
      return
    }
    
    setCorpDeadbeatsRows([]);
    axios.get(`/corporation/${activeCorporationId.toString()}/deadbeats`)
      .then(res => {
        const deadbeats = res.data.deadbeats;
        const rows = deadbeats.map((charName, index) => (
          <Table.Tr key={index}>
            <Table.Td>{charName}</Table.Td>
          </Table.Tr>
        ));
        setCorpDeadbeatsRows(rows)
      }).catch(error => {
        showNotification({
          message: "Error fetching possible deadbeats",
          ...negaNotifProps
        })
        console.error("Error fetching possible deadbeats: ", error);
      })
  }, [activeCorporationId])

  return (
    <div className="App">
      <Menu />
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
      <Tabs variant="pills" defaultValue="overview">
        <Tabs.List className="corporationTabsList">
          <Tooltip
            multiline
            w={"13vw"}
            transitionProps={{ duration: 150 }}
            label="Data in chart is not limited to the Sigma Grindset alliance. Character information is limited to Sigma kills"
          >
            <Tabs.Tab value="overview" leftSection={<IconListTree />}>
              Overview
            </Tabs.Tab>
          </Tooltip>
          <Tooltip
            multiline
            w={"13vw"}
            transitionProps={{ duration: 150 }}
            label="Possible deadbeats are defined as; characters who have gotten a kill in the past 6 months, but not in the past 2 months."
          >
            <Tabs.Tab value="lastMonth" leftSection={<IconCalendarMonth />}>
              Last month
            </Tabs.Tab>
          </Tooltip>
        </Tabs.List>

        <Tabs.Panel value="overview">
          <div className="corpOverviewFocus">
            <div className="viewGraph">
              <LineChart
                data={monthsData}
                dataKey={"monthYearConcat"}
                series={[
                  { name: `${displayOptionsDropdownText.toLowerCase()}Destroyed`, color: '#82ca9d' },
                  { name: `${displayOptionsDropdownText.toLowerCase()}Lost`, color: '#b64949' },
                ]}
                curveType="bump"
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
        </Tabs.Panel>
        <Tabs.Panel value="lastMonth">
          <div className="corpLastMonthFocus">
            <div>
              <h5 className="tableTitle">
                Top killers past month
              </h5>
              <Table.ScrollContainer minWidth={"13vw"} className="corpTableLastMonth">
                <Table horizontalSpacing="md">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Character</Table.Th>
                      <Table.Th style={{textAlign: 'right'}}>Kills</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>{corpLastMonthKillRows}</Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </div>
            <div>
              <h5 className="tableTitle">
                Characters who did not get 10+ kills past month
              </h5>
              <Table.ScrollContainer minWidth={"13vw"} className="corpTableLastMonth">
                <Table horizontalSpacing="md">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Character</Table.Th>
                      <Table.Th style={{textAlign: 'right'}}>Kills</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>{corpLastMonthLowKillRows}</Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </div>
            <div>
              <h5 className="tableTitle">
                Possible deadbeats
              </h5>
              <Table.ScrollContainer minWidth={"13vw"} className="corpTableLastMonth">
                <Table horizontalSpacing="md">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Character</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>{corpDeadbeatsRows}</Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </div>
          </div>          
        </Tabs.Panel>
      </Tabs>
    </div>
  );
}