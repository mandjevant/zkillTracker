// The idea:
// An interactive graph for alliance table.
// Multiselect the corporations to show as lines
/// Toggle alliance total or depict this elsewhere
// Dropdown for Kills, Mains, ActiveMains, KillsPerActiveMain, PercentageOfAllianceKills

import React, { useState, useEffect } from 'react';
import Menu from './menu';
import { MultiSelect, Select, Box, Text } from '@mantine/core';
import { MonthPickerInput } from '@mantine/dates';
import { LineChart } from '@mantine/charts';
import { negaNotifProps } from './helpers';
import { showNotification } from '@mantine/notifications';
import { useAuth } from '../App';


export default function AllianceView() {
  const today = new Date();
  const lyMonth = new Date(today.getFullYear() - 1, today.getMonth(), 1);
  const curMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  const displayOptions = ["kills", "mains", "activeMains", "killsPerActiveMain", "percentageOfAllianceKills", "growthRate"]
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

  const [allTickers, setAllTickers] = useState([])
  const [monthRange, setMonthRange] = useState([lyMonth, curMonth])
  const [selectedCorporations, setSelectedCorporations] = useState(["MCAP"])
  const [displayOption, setDisplayOption] = useState("killsPerActiveMain")
  const [allianceChartData, setAllianceChartData] = useState([])
  const { axiosInstance } = useAuth();

  useEffect(() => {
    if (!monthRange[0] | !monthRange[1]) {
      return
    }

    const params = new URLSearchParams({
      start_year: monthRange[0].getFullYear(),
      start_month: monthRange[0].getMonth(),
      end_year: monthRange[1].getFullYear(),
      end_month: monthRange[1].getMonth(),
    });

    axiosInstance.get(`/get_alliance_tickers?${params.toString()}`)
      .then(res => {
        const corpTickers = res.data.map(i => i.corporationTicker).sort()
        const uniqCorpTickers = [...new Set(corpTickers)]
        if (uniqCorpTickers.includes("5IGMA")) {
          uniqCorpTickers.splice(uniqCorpTickers.indexOf("5IGMA"), 1)
          const data = [
            { group: "Corporations", items: uniqCorpTickers },
            { group: "Alliance", items: ["5IGMA"] },
          ]
          setAllTickers(data);
        } else {
          setAllTickers(uniqCorpTickers);
        }
      })
      .catch(error => {
        showNotification({
          message: "Error fetching alliance tickers",
          ...negaNotifProps
        })
        console.error("Error fetching alliance tickers: ", error);
      });
  }, [monthRange, axiosInstance]);

  useEffect(() => {
    if (!monthRange[0] | !monthRange[1] | !selectedCorporations) {
      return
    }

    const params = new URLSearchParams({
      start_year: monthRange[0].getFullYear(),
      start_month: monthRange[0].getMonth(),
      end_year: monthRange[1].getFullYear(),
      end_month: monthRange[1].getMonth(),
    })

    selectedCorporations.forEach(corp => params.append('corporations', corp));

    axiosInstance.get(`/get_alliance_data?${params.toString()}`)
      .then(res => {
        const allianceWithMonthYearConcat = res.data.map(entry => {
          return {
            ...entry,
            monthYearConcat: `${entry.month}-${entry.year}`
          };
        });

        const dict = {};

        allianceWithMonthYearConcat.forEach(item => {
          // eslint-disable-next-line
          const { monthYearConcat, corporationTicker, kills, mains, activeMains, killsPerActiveMain, percentageOfAllianceKills, growthRate } = item;

          if (!dict[monthYearConcat]) {
            dict[monthYearConcat] = {};
          }

          //eslint-disable-next-line
          dict[monthYearConcat][corporationTicker] = eval(displayOption);
        });

        const output = Object.keys(dict).map(monthYearConcat => {
          const result = { monthYearConcat };

          selectedCorporations.forEach(ticker => {
            result[ticker] = dict[monthYearConcat][ticker] !== undefined ? dict[monthYearConcat][ticker] : null;
          });

          return result;
        });

        output.sort((a, b) => {
          const [aMonth, aYear] = a.monthYearConcat.split('-').map(Number);
          const [bMonth, bYear] = b.monthYearConcat.split('-').map(Number);

          if (aYear !== bYear) {
            return aYear - bYear;
          }
          return aMonth - bMonth;
        });

        setAllianceChartData(output);
      })
      .catch(error => {
        showNotification({
          message: "Error fetching alliance data",
          ...negaNotifProps
        })
        console.error("Error fetching alliance data: ", error);
      });
  }, [monthRange, selectedCorporations, displayOption, axiosInstance])


  function ChartLegend() {
    return (
      <Box className="customAllianceLegend">
        {selectedCorporations.map((corp, index) => (
          <Text className="legendItem" key={index} c={colors[index]} fz="sm">
            ● {corp}
          </Text>
        ))}
      </Box>
    );
  }

  return (
    <div className="App">
      <Menu />
      <div className="viewGraph" id="allianceGraph">
        <LineChart
          id="allianceLineChart"
          data={allianceChartData}
          dataKey={"monthYearConcat"}
          series={selectedCorporations.map((corp, index) => (
            { name: corp, color: colors[index], alwaysShowInLegend: true }
          ))}
          curveType="bump"
          withLegend
          legendProps={{ content: <ChartLegend />, }}
          tooltipAnimationDuration={100}
          xAxisLabel={"Month-Year"}
          yAxisLabel={displayOption}
        />
        <div className="allianceGraphSelectors">
          <MonthPickerInput
            type="range"
            label="Pick date range"
            placeholder="Pick date range"
            value={monthRange}
            onChange={setMonthRange}
          />
          <MultiSelect
            checkIconPosition="right"
            label="Corporations to show"
            data={allTickers}
            searchable
            defaultValue={["MCAP"]}
            onChange={setSelectedCorporations}
          />
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
    </div>
  )
}