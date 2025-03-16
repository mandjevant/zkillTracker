import { useEffect, useState } from 'react';
import { negaNotifProps } from './helpers';
import { showNotification } from '@mantine/notifications';
import { Table } from '@mantine/core';
import { useAuth } from '../App';


export default function AllianceLastMonth(props) {
  const { axiosInstance } = useAuth();
  const [allianceDataRows, setAllianceDataRows] = useState([])
  const { displayOptions } = props;

  useEffect(() => {
    axiosInstance.get(`/alliance/lastmonth`)
      .then(res => {
        setAllianceDataRows(
          Object.entries(res.data).map(([inx, obj], index) => (
            <Table.Tr key={inx}>
              <Table.Td>{obj.corporationTicker}</Table.Td>
              <Table.Td>{obj.kills}</Table.Td>
              <Table.Td>{obj.mains}</Table.Td>
              <Table.Td>{obj.activeMains}</Table.Td>
              <Table.Td>{obj.killsPerActiveMain}</Table.Td>
              <Table.Td>{obj.percentageOfAllianceKills}</Table.Td>
            </Table.Tr>
          )) 
        )
      })
      .catch(err => {
        showNotification({
          message: `Error fetching last month alliance data, ${err}`,
          ...negaNotifProps,
        })
      })
  }, [axiosInstance]);

  return (
    <div className="viewGraph">
      <Table.ScrollContainer minWidth={"13vw"} className="allianceTable">
        <Table stickyHeader horizontalSpacing="md">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Corporation</Table.Th>
              {displayOptions.map((option, idx) => (
                <Table.Th key={idx}>{option}</Table.Th>
              ))}
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{allianceDataRows}</Table.Tbody>
        </Table>
      </Table.ScrollContainer>
    </div>
  )
}
