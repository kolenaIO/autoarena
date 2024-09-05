import { ChartTooltipProps, LineChart } from '@mantine/charts';
import { useMemo } from 'react';
import { LoadingOverlay, Paper, Stack, Title, Grid, Box } from '@mantine/core';
import { IconCactus } from '@tabler/icons-react';
import { EloHistoryItem, useModelEloHistory } from '../../hooks/useModelEloHistory.ts';
import { NonIdealState } from '../NonIdealState.tsx';
import { useUrlState } from '../../hooks/useUrlState.ts';

type ChartDatum = EloHistoryItem & { position: number };

type Props = {
  modelId: number;
};
export function EloHistoryPlot({ modelId }: Props) {
  const { judgeId } = useUrlState();
  const { data: eloHistory, isLoading } = useModelEloHistory(modelId, judgeId);

  const chartData: ChartDatum[] = useMemo(
    () => (eloHistory ?? []).map((item, i) => ({ position: i + 1, ...item })),
    [eloHistory]
  );
  const [minElo, maxElo] = useMemo(
    () =>
      (eloHistory ?? []).reduce(
        ([prevMin, prevMax], { elo }) => [Math.min(prevMin, elo), Math.max(prevMax, elo)],
        [Infinity, -Infinity]
      ),
    [eloHistory]
  );

  return (
    <Paper p="xs" radius="md" withBorder>
      <Stack align="center" style={{ position: 'relative' }}>
        <Title order={6}>Elo Score History</Title>
        <LineChart
          h={300}
          withDots={false}
          data={chartData}
          dataKey="position"
          series={[{ name: 'elo', color: 'kolena.4' }]}
          valueFormatter={value => value.toFixed(1)}
          curveType="bump"
          xAxisLabel="# Head-to-Heads"
          xAxisProps={{ minTickGap: 20 }}
          yAxisLabel="Elo Score"
          yAxisProps={{ domain: [minElo, maxElo] }}
          tooltipProps={{ content: ({ payload }) => <EloHistoryPlotTooltip payload={payload} /> }}
        />
        <LoadingOverlay visible={isLoading} overlayProps={{ radius: 'md', blur: 4 }} />
        <Box hidden={isLoading || (eloHistory?.length ?? 0) > 0} style={{ position: 'absolute', top: '25%' }}>
          <NonIdealState IconComponent={IconCactus} description="No History to display" />
        </Box>
      </Stack>
    </Paper>
  );
}

function EloHistoryPlotTooltip({ payload }: Pick<ChartTooltipProps, 'payload'>) {
  const datum: ChartDatum = payload?.[0]?.payload;
  if (datum == null) {
    return <></>;
  }
  return (
    <Paper withBorder shadow="sm" radius="md" p="xs" fz="xs">
      <Grid gutter={2} w={250}>
        <Grid.Col span={4} fw="bold">
          Round
        </Grid.Col>
        <Grid.Col span={8}>{datum.position.toLocaleString()}</Grid.Col>
        <Grid.Col span={4} fw="bold">
          Judge
        </Grid.Col>
        <Grid.Col span={8}>{datum.judge_name}</Grid.Col>
        <Grid.Col span={4} fw="bold">
          Opponent
        </Grid.Col>
        <Grid.Col span={8}>{datum.other_model_name}</Grid.Col>
        <Grid.Col span={4} fw="bold">
          Elo Score
        </Grid.Col>
        <Grid.Col span={8}>{datum.elo.toFixed(1)}</Grid.Col>
      </Grid>
    </Paper>
  );
}
