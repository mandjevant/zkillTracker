import { MultiSelect, Select } from '@mantine/core';
import { useState, useEffect } from 'react';
import { LineChart } from '@mantine/charts';
import { useAuth } from '../App';
import { negaNotifProps } from './helpers';
import { showNotification } from '@mantine/notifications';


export default function MultiselectMembers(props) {
  const [corporationChoice, setCorporationChoice] = useState(null);
  const [memberList, setMemberList] = useState([]);
  const [memberNamesList, setMemberNamesList] = useState([]);
  const [displayOption, setDisplayOption] = useState("killCount");
  const [allMembers, setAllMembers] = useState([]);
  const [multiMemberChartData, setMultiMemberChartData] = useState([]);
  const { allCorporations, displayOptions, formatFinancial, formatInteger } = props;
  const colors = [
    "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
    "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF",
    "#AEC7E8", "#FFBB78", "#98DF8A", "#FF9896", "#C5B0D5",
    "#C49C94", "#F7B6D2", "#C7C7C7", "#DBDB8D", "#9EDAE5",
    "#393B79", "#637939", "#8C6D31", "#843C39", "#7B4173",
    "#5254A3", "#8CA252", "#BD9E39", "#AD494A", "#A55194",
    "#6B6ECF", "#B5CF6B", "#E7BA52", "#D6616B", "#CE6DBD",
    "#9C9EDE", "#CEDB9C", "#E7CB94", "#E7969C", "#DE9ED6",
    "#393B79", "#637939", "#8C6D31", "#843C39", "#7B4173",
    "#5254A3", "#8CA252", "#BD9E39", "#AD494A", "#A55194"
  ];
  const { axiosInstance } = useAuth()

  useEffect(() => {
    if (!corporationChoice) {
      return
    }
    axiosInstance.get(`/corporation/${parseInt(corporationChoice)}/members`)
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
  }, [corporationChoice, axiosInstance]);

  useEffect(() => {
    if (memberList.length === 0) {
      return
    }
    const params = new URLSearchParams({});
    memberList.forEach(member => params.append('members', member));

    axiosInstance.get(`/members/${displayOption}/stats?${params.toString()}`)
      .then(res => {
        const data = res.data;
        const dict = {};

        Object.entries(data).forEach(([characterId, stats]) => {
          Object.values(stats).forEach(val => {
            // eslint-disable-next-line
            const { killCount, totalValue, solo, awox, npc, points, year_month } = val;
            
            if (!dict[year_month]) {
              dict[year_month] = {};
            }

            //eslint-disable-next-line
            dict[year_month][characterId] = eval(displayOption);
          })
        });

        const idToLabel = Object.fromEntries(allMembers.map(({ value, label }) => [value, label]));
        const translatedOutput = Object.keys(dict).map(monthYearConcat => {
          const result = { monthYearConcat };

          memberList.forEach(memberId => {
            result[idToLabel[memberId] || memberId] = dict[monthYearConcat][memberId];
          });

          return result;
        })

        setMemberNamesList(Object.keys(translatedOutput[0]).filter(key => key !== "monthYearConcat"));
        setMultiMemberChartData(translatedOutput);
      })
      .catch(error => {
        showNotification({
          message: "Could not load multi member data",
          ...negaNotifProps
        })
      })
  }, [memberList, corporationChoice, axiosInstance, displayOption, allMembers])

  return (
    <div className="multiMemberTab">
      <div className='test'>
        <LineChart
          id="memberLineChart"
          data={multiMemberChartData}
          dataKey={"monthYearConcat"}
          series={memberNamesList.map((member, index) => (
            { name: member, color: colors[index], alwaysShowInLegend: true }
          ))}
          curveType="bump"
          withLegend
          tooltipAnimationDuration={100}
          xAxisLabel={"Month-Year"}
          yAxisLabel={displayOption}
          valueFormatter={displayOption === "totalValue" ? formatFinancial : formatInteger}
        />
      </div>
      <div>
        <Select
          className="newMemberSelector"
          checkIconPosition="right"
          label="Choose corporation"
          placeholder=""
          data={allCorporations}
          searchable
          defaultValue={[""]}
          onChange={setCorporationChoice}
          allowDeselect={false}
        />
        <MultiSelect
          className="newMemberSelector2"
          checkIconPosition="right"
          label="Choose members"
          data={allMembers}
          searchable
          defaultValue={[]}
          onChange={setMemberList}
        />
        <Select
          className="newMemberSelector2"
          checkIconPosition="right"
          label="Choose statistic for multiselect chart"
          placeholder="killCount"
          data={displayOptions}
          searchable
          defaultValue={["killCount"]}
          onChange={setDisplayOption}
          allowDeselect={false}
        />
      </div>
    </div>
  )
}