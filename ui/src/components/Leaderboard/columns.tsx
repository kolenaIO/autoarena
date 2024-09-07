import { DataTableColumn } from 'mantine-datatable';
import { Box, Button, ButtonGroup, Code } from '@mantine/core';
import { v4 as uuidv4 } from 'uuid';
import { useMemo, useState } from 'react';
import { Model, ModelExtraStats } from '../../hooks/useModels.ts';
import { EloWidget } from './EloWidget.tsx';
import { RankedModel } from './types.ts';
import { ModelNameRenderer } from './renderers/ModelNameRenderer.tsx';

export const LOADING_MODELS: Model[] = Array(16)
  .fill(null)
  .map((_, i) => {
    const elo = 1000 + (0.5 - Math.random()) * 1000;
    return {
      id: i,
      name: uuidv4().substring(0, 10 + Math.random() * 25),
      created: new Date().toString(),
      elo,
      q025: elo - Math.random() * 50,
      q975: elo + Math.random() * 50,
      datapoints: 500 + Math.random() * 1000,
      votes: Math.floor(elo),
      extra_stats: {},
    };
  })
  .sort((a, b) => b.elo - a.elo);

export const LEADERBOARD_COLUMNS: DataTableColumn<RankedModel>[] = [
  { accessor: 'rank', sortable: true },
  { accessor: 'name', sortable: true, render: ModelNameRenderer },
  {
    accessor: 'elo-widget',
    title: '',
    render: ({ elo, q025, q975, globalLo, globalHi }) =>
      q025 != null && q975 != null ? (
        <EloWidget elo={elo} qLo={q025} qHi={q975} globalLo={globalLo} globalHi={globalHi} />
      ) : undefined,
  },
  { accessor: 'elo', sortable: true, render: ({ elo }) => <Code>{elo.toFixed(1)}</Code> },
  {
    accessor: 'q025',
    title: 'CI 95%',
    render: ({ elo, q025, q975 }) =>
      q025 != null &&
      q975 != null && (
        <Box miw={80}>
          <Code>
            +{(q975 - elo).toFixed(0)} / -{(elo - q025).toFixed(0)}
          </Code>
        </Box>
      ),
  },
  {
    accessor: 'datapoints',
    sortable: true,
    title: '# Datapoints',
    render: ({ datapoints }) => datapoints.toLocaleString(),
  },
  { accessor: 'votes', sortable: true, title: '# Votes', render: ({ votes }) => votes.toLocaleString() },
];

export function useLeaderboardColumns(models: Model[] | undefined) {
  const [selectedStats, setSelectedStats] = useState<Record<string, keyof ModelExtraStats>>({});
  const extraColumns = useMemo(
    () => [...new Set((models ?? []).flatMap(({ extra_stats }) => Object.keys(extra_stats)))],
    [models]
  );

  function setSelectedStat(name: string, stat: keyof ModelExtraStats) {
    setSelectedStats(prev => ({ ...prev, [name]: stat }));
  }

  return [
    ...LEADERBOARD_COLUMNS,
    ...extraColumns.map<DataTableColumn<RankedModel>>(name => {
      const selectedStat = selectedStats[name] ?? 'mean';
      return {
        accessor: `extra_stats.${name}.${selectedStat}`,
        title: name,
        sortable: true,
        render: obj => obj.extra_stats[name]?.[selectedStat]?.toFixed(1),
        filter: ({ close }) => {
          const stats = {
            mean: 'Mean',
            median: 'Median',
            stdev: 'Standard Deviation',
            sum: 'Sum',
            max: 'Max',
            min: 'Min',
          };
          return (
            <ButtonGroup orientation="vertical">
              {Object.entries(stats).map(([stat, statDisplayName]) => (
                <Button
                  size="xs"
                  key={stat}
                  color={selectedStat === stat ? 'kolena' : 'gray'}
                  variant={selectedStat === stat ? 'light' : 'subtle'}
                  justify="flex-start"
                  onClick={() => {
                    // cast because Object.entries always returns string keys
                    setSelectedStat(name, stat as keyof ModelExtraStats);
                    close();
                  }}
                >
                  {statDisplayName}
                </Button>
              ))}
            </ButtonGroup>
          );
        },
      };
    }),
  ];
}
