import { useState, useEffect } from 'react';
import { negaNotifProps } from './helpers';
import { showNotification } from '@mantine/notifications';
import { Table, Select } from '@mantine/core';
import { useAuth } from '../App';


export default function AllianceSixMonths(props) {
  const [allianceDataRows, setAllianceDataRows] = useState([])
  const [sigmaDataRow, setSigmaDataRow] = useState([])
  const [displayOption, setDisplayOption] = useState("killsPerActiveMain")
  const { displayOptions } = props;
  const { axiosInstance } = useAuth();

  const now = new Date();
  const yearMonths = [...Array(6)].map((_, i) => {
    const tempDate = new Date(now);
    tempDate.setMonth(now.getMonth() - (5 - i));
    return `${tempDate.getFullYear()}-${String(tempDate.getMonth() + 1).padStart(2, '0')}`;
  });

  useEffect(() => {
    axiosInstance.get(`/alliance/${displayOption}/sixmonths`)
      .then(res => {
        const allCorps = res.data
        Object.entries(res.data).forEach(([corpTicker, arr]) => {
          if (corpTicker === "5IGMA") {
            setSigmaDataRow(
              <Table.Tr>
                <Table.Th>5IGMA</Table.Th>
                {arr.map((val, idx) => (
                  <Table.Th key={idx} style={{ textAlign: "right" }}>
                    {displayOption === "percentageOfAllianceKills" ? parseFloat(val).toFixed(2) : parseFloat(val).toFixed(1)}
                  </Table.Th>
                ))}
              </Table.Tr>
            );
            delete allCorps[corpTicker]
          }
        })

        setAllianceDataRows(
          Object.entries(allCorps).map(([corpTicker, arr], index) => (
            <Table.Tr key={index}>
              <Table.Td>{corpTicker}</Table.Td>
              {arr.map((val, idx) => (
                <Table.Td key={idx} style={{ textAlign: "right" }}>
                  {displayOption === "percentageOfAllianceKills" ? parseFloat(val).toFixed(2) : parseFloat(val).toFixed(1)}
                </Table.Td>
              ))}
            </Table.Tr>
          ))
        );
      })
      .catch(err => {
        showNotification({
          message: `Error fetching past six months alliance data ${err}`,
          ...negaNotifProps,
        })
        console.error("Error fetching past six months alliance data: ", err)
      })
  }, [displayOption, axiosInstance])

  return (
    <div className="viewGraph">
      <Table.ScrollContainer minWidth={"13vw"} className="allianceTable">
        <Table stickyHeader horizontalSpacing="md">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Corporation</Table.Th>
              {yearMonths.map((monthYearConcat, idx) => (
                <Table.Th key={idx}>{monthYearConcat}</Table.Th>
              ))}
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{allianceDataRows}</Table.Tbody>
          <Table.Tfoot>{sigmaDataRow}</Table.Tfoot>
        </Table>
      </Table.ScrollContainer>
      <div className="allianceGraphSelectors">
        <Select
          checkIconPosition="right"
          label="Choose statistic"
          placeholder="killsPerActiveMain"
          data={displayOptions}
          searchable
          defaultValue={["killsPerActiveMain"]}
          onChange={setDisplayOption}
          allowDeselect={false}
        />
      </div>
    </div>
  )
}