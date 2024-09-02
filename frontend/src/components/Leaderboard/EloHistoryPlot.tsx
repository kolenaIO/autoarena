import { LineChart } from '@mantine/charts';
import { useMemo } from 'react';
import { LoadingOverlay, Paper, Stack, Title } from '@mantine/core';
import { useModelEloHistory } from '../../hooks/useModelEloHistory.ts';

type Props = {
  modelId: number;
};
export function EloHistoryPlot({ modelId }: Props) {
  const { data: eloHistory, isLoading } = useModelEloHistory(modelId);

  const chartData = useMemo(() => (eloHistory ?? []).map((elo, i) => ({ battle: i + 1, elo })), [eloHistory]);
  const [minElo, maxElo] = useMemo(
    () =>
      (eloHistory ?? []).reduce(
        ([prevMin, prevMax], elo) => [Math.min(prevMin, elo), Math.max(prevMax, elo)],
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
          data={chartData}
          withDots={false}
          withTooltip={false}
          dataKey="battle"
          title="Elo Score History"
          yAxisLabel="Elo Score"
          yAxisProps={{ domain: [minElo, maxElo] }}
          valueFormatter={value => value.toFixed(1)}
          xAxisLabel="# Head-to-Heads"
          series={[{ name: 'elo', color: 'kolena.4' }]}
          curveType="bump"
        />
        <LoadingOverlay visible={isLoading} overlayProps={{ radius: 'md', blur: 4 }} />
      </Stack>
    </Paper>
  );
}
