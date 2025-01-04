import { useState, useEffect, useCallback } from 'react'
import Menu from './menu';
import { IconCalendarMonth, IconInfinity } from '@tabler/icons-react';
import { Tabs, Select, Paper, Table, Button, NumberFormatter, Tooltip } from '@mantine/core';
import axios from 'axios';
import { negaNotifProps } from './helpers';
import { showNotification } from '@mantine/notifications';
import { LineChart } from '@mantine/charts';


export default function MemberView() {
  const [allCorporations, setAllCorporations] = useState([])
  const [allMembers, setAllMembers] = useState([])
  const [focusedCorporation, setFocusedCorporation] = useState(null)
  const [focusedMember, setFocusedMember] = useState(null)
  const [monthlyAggKillData, setMonthlyAggKillData] = useState([])
  const [focusedCharName, setFocusedCharName] = useState('')
  const [focusedAllKills, setFocusedAllKills] = useState(0)
  const [focusedCurMonthKillsRows, setFocusedCurMonthKillsRows] = useState([])
  const [focusedCurMonthAllKills, setFocusedCurMonthAllKills] = useState(0)
  const [focusedPrevMonthAllKills, setFocusedPrevMonthAllKills] = useState(0)
  const [allItems, setAllItems] = useState([])
  const [displayOption, setDisplayOption] = useState("killCount")
  const displayOptions = ["killCount", "totalValue", "solo", "awox", "npc", "points"]
  const formatFinancial = (value) => `$${Math.round(value).toLocaleString()}`;
  const formatInteger = (value) => Math.round(value).toLocaleString();

  useEffect(() => {
    axios.get("/corporations")
      .then(res => {
        const mappedCorps = res.data.map(corp => ({
          value: corp.id.toString(),
          label: corp.name
        }));
        setAllCorporations(mappedCorps);
      })
      .catch(error => {
        console.error("Error fetching corporations: ", error);
      });
    
    axios.get("/items")
      .then(res => {
        setAllItems(res.data)
      })
      .catch(error => {
        console.error("Error fetching items: ", error);
      });
  }, []);

  const getCharacterName = useCallback((characterID) => {
    const member = allMembers.find(
      char => char.value === characterID.toString()
    );
    return member ? member.label : '';
  }, [allMembers])

  useEffect(() => {
    if (!focusedCorporation) {
      return
    }
    axios.get(`/corporation/${parseInt(focusedCorporation)}/members`)
      .then(res => {
        const mappedMembers = res.data.map(char => ({
          value: char.characterID.toString(),
          label: char.characterName
        }));
        setAllMembers(mappedMembers);
      })
      .catch(error => {
        if (error.response?.status === 404) {
          showNotification({
            message: error.response.data.error,
            ...negaNotifProps
          })
        } else {
          console.error("Error fetching members: ", error);
        }
      });
  }, [focusedCorporation]);

  useEffect(() => {
    if (!focusedMember) {
      return
    }
    axios.get(`/member/${focusedMember}/monthlyaggregations`)
      .then(res => {
        setMonthlyAggKillData(res.data);

        const name = getCharacterName(focusedMember);
        setFocusedCharName(name);
      })
      .catch(error => {
        if (error.response?.status === 404) {
          showNotification({
            message: error.response.data.error,
            ...negaNotifProps
          })
        } else {
          console.error("Error fetching member data: ", error);
        }
      });
  }, [focusedMember, allMembers, getCharacterName]);

  useEffect(() => {
    if (!focusedMember) {
      return
    }
    setFocusedAllKills(0)
    axios.get(`/member/${focusedMember}/kills/all`)
      .then(res => {
        setFocusedAllKills(res.data.length);
      })
      .catch(error => {
        if (error.response?.status === 404) {
          showNotification({
            message: error.response.data.error,
            ...negaNotifProps
          });
        } else {
          console.error("Error fetching member data: ", error);
        }
      });
  }, [focusedMember])

  const getItemName = useCallback((typeId) => {
    const item = allItems.find(item => item.type_id === typeId);
    return item ? item.name : typeId;
  }, [allItems])

  useEffect(() => {
    if (!focusedMember) {
      return
    }
    const curYear = new Date().getFullYear()
    const curMonth = new Date().getMonth()
    const prevDate = new Date(new Date().setMonth(curMonth-1))
    const prevYear = prevDate.getFullYear()
    const prevMonth = prevDate.getMonth()

    setFocusedCurMonthKillsRows([]);
    setFocusedCurMonthAllKills(0);
    setFocusedPrevMonthAllKills(0);

    axios.get(`/member/${focusedMember}/kills/year/${curYear}/month/${curMonth+1}`)
      .then(res => {
        setFocusedCurMonthAllKills(res.data.length);

        const rows = res.data.map((kill) => (
          <Table.Tr key={kill.killID} onDoubleClick={() => window.open(`https://zkillboard.com/kill/${kill.killID}/`, '_blank')}>
            <Table.Td>{getItemName(kill.shipTypeID)}</Table.Td>
            <Table.Td >
              <NumberFormatter value={kill.damageDone} thousandSeparator />
            </Table.Td>
            <Table.Td>{kill.finalBlow}</Table.Td>
            <Table.Td>{getItemName(kill.attackerShipTypeID)}</Table.Td>
            <Table.Td>{kill.solo}</Table.Td>
            <Table.Td>{`https://zkillboard.com/kill/${kill.killID}/`}</Table.Td>
          </Table.Tr>
        ));
        setFocusedCurMonthKillsRows(rows);
      })
      .catch(error => {
        if (error.response?.status === 404) {
          showNotification({
            message: "No kills found for the specified member current month",
            ...negaNotifProps
          });
        } else {
          console.error("Error fetching kills current month: ", error);
        }
      });

    axios.get(`/member/${focusedMember}/kills/year/${prevYear}/month/${prevMonth+1}`)
      .then(res => {
        setFocusedPrevMonthAllKills(res.data.length);
      })
      .catch(error => {
        if (error.response?.status === 404) {
          showNotification({
            message: "No kills found for the specified member previous month",
            ...negaNotifProps
          });
        } else {
          console.error("Error fetching kills previous month: ", error);
        }
      });
  }, [focusedMember, getItemName])

  return (
    <div className="App">
      <Menu />
      <div className="memberView">
        <div className="viewWindow">
          <Tabs variant="pills" defaultValue="monthly">
            <Tabs.List>
              <Tooltip
                multiline
                w={"13vw"}
                transitionProps={{ duration: 150 }}
                label="Only includes Sigma kills, but from any corporation. There may be a delay (up to 4 weeks) after a character joins/switches corporation. Blame evewho :)"
              >
                <Tabs.Tab value="monthly" leftSection={<IconCalendarMonth />}>
                  Monthly
                </Tabs.Tab>
              </Tooltip>
              <Tabs.Tab value="totals" leftSection={<IconInfinity />}>
                Totals
              </Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="monthly">
              <LineChart
                id="memberLineChart"
                data={monthlyAggKillData}
                dataKey={"year_month"}
                series={[
                  { 
                    name: displayOption, 
                    color: "#1F77B4", 
                  }
                ]}
                curveType="bump"
                withLegend
                tooltipAnimationDuration={100}
                xAxisLabel={"Month-Year"}
                yAxisLabel={displayOption}
                valueFormatter={displayOption === "totalValue" ? formatFinancial : formatInteger}
              />
            </Tabs.Panel>

            <Tabs.Panel value="totals">
              <div className="charNameLink">
                <h2>{focusedCharName ? focusedCharName : "Name"}</h2>
                <Button
                  className="zkillLinkButton"
                  onClick={() => window.open(
                    `https://zkillboard.com/character/${focusedMember}/`, '_blank')}
                  disabled={!focusedMember}
                >
                  {focusedCharName ? `To zkill: ${focusedCharName}` : 'Zkill link'}
                </Button>
              </div>
              <div className="papers">
                <Paper className="memberTotalsPaper" shadow="xs" withBorder p="xs">
                  <h4>Total kills in Sigma</h4>
                  <p>{focusedAllKills}</p>
                </Paper>
                <Paper className="memberTotalsPaper" shadow="xs" withBorder p="xs">
                  <h4>Kills this month</h4>
                  <p>{focusedCurMonthAllKills}</p>
                </Paper>
                <Paper className="memberTotalsPaper" shadow="xs" withBorder p="xs">
                  <h4>Kills last month</h4>
                  <p>{focusedPrevMonthAllKills}</p>
                </Paper>
              </div>
              <div className="table">
                <h5 className="tableTitle">
                  Detailed kills this month. Double click for zkill link
                </h5>
                <Table.ScrollContainer minWidth={500}>
                  <Table>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Killed ship</Table.Th>
                        <Table.Th>Damage done</Table.Th>
                        <Table.Th>Final blow</Table.Th>
                        <Table.Th>Attacker ship</Table.Th>
                        <Table.Th>Solo</Table.Th>
                        <Table.Th>Zkill link</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>{focusedCurMonthKillsRows}</Table.Tbody>
                  </Table>
                </Table.ScrollContainer>
              </div>
            </Tabs.Panel>
          </Tabs>
        </div>
        <div className="memberSelectors">
          <Select
            className="memberSelector"
            checkIconPosition="right"
            label="Choose corporation"
            placeholder=""
            data={allCorporations}
            searchable
            defaultValue={[""]}
            onChange={setFocusedCorporation}
            allowDeselect={false}
          />
          <Select
            className="memberSelector"
            checkIconPosition="right"
            label="Choose member"
            placeholder=""
            data={allMembers}
            searchable
            defaultValue={[""]}
            onChange={setFocusedMember}
            allowDeselect={false}
          />
          <Select
            className="memberSelector"
            checkIconPosition="right"
            label="Choose statistic for monthly chart"
            placeholder="killCount"
            data={displayOptions}
            searchable
            defaultValue={["killCount"]}
            onChange={setDisplayOption}
            allowDeselect={false}
          />
        </div>
      </div>
    </div>
  )
}