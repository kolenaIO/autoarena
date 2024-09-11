import { DataTableColumn } from 'mantine-datatable';
import { Box, Code, Text, Tooltip } from '@mantine/core';
import { v4 as uuidv4 } from 'uuid';
import { Model } from '../../hooks/useModels.ts';
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
      n_responses: 500 + Math.random() * 1000,
      n_votes: Math.floor(elo),
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
    // TODO: add tooltip explaining 95% confidence interval
    title: (
      <Tooltip label="95% Confidence Interval">
        <Text size="sm" fw="bold">
          CI 95%
        </Text>
      </Tooltip>
    ),
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
    accessor: 'n_responses',
    sortable: true,
    title: '# Responses',
    render: ({ n_responses }) => n_responses.toLocaleString(),
  },
  {
    accessor: 'n_votes',
    sortable: true,
    title: '# Votes',
    render: ({ n_votes }) => n_votes.toLocaleString(),
  },
];
