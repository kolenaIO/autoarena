import { BarChart } from '@mantine/charts';
import { Box, Checkbox, Group, LoadingOverlay, Paper, Stack, Title, Text } from '@mantine/core';
import { useMemo, useState } from 'react';
import { prop, sortBy } from 'ramda';
import { IconCactus } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useModelHeadToHeadStatsByJudge } from '../../hooks/useModelHeadToHeadStatsByJudge.ts';
import { NonIdealState } from '../NonIdealState.tsx';
import { useJudge } from '../../hooks/useJudge.ts';

type ChartRecord = {
  opponentName: string;
  opponentId: number;
  nWins: number;
  nLosses: number;
  nTies: number;
  sortSlug: string;
};

type Props = {
  modelId: number;
};
export function HeadToHeadStatsPlot({ modelId }: Props) {
  const { projectSlug = '', judgeId } = useUrlState();
  const navigate = useNavigate();
  const { data: judge } = useJudge(projectSlug, judgeId);
  const { data: headToHeadStats, isLoading } = useModelHeadToHeadStatsByJudge({ projectSlug, modelId, judgeId });
  const [isPercentage, setIsPercentage] = useState(true);

  const plotStats = useMemo(() => {
    const statsFiltered = (headToHeadStats ?? []).filter(({ judge_id }) => judgeId == null || judge_id === judgeId);
    const statsEnhanced = statsFiltered.reduce<{ [opponentName: string]: ChartRecord }>((acc, s) => {
      const existing = acc[s.other_model_name] ?? { nWins: 0, nLosses: 0, nTies: 0 };
      const countJudge = s.count_wins + s.count_ties + s.count_losses;
      const countExisting = existing.nWins + existing.nLosses + existing.nTies;
      const countTotal = countExisting + countJudge;
      const winPercentage = (existing.nWins + s.count_wins) / countTotal;
      const tiePercentage = (existing.nTies + s.count_ties) / countTotal;
      return {
        ...acc,
        [s.other_model_name]: {
          opponentName: s.other_model_name,
          opponentId: s.other_model_id,
          nWins: existing.nWins + s.count_wins,
          nLosses: existing.nLosses + s.count_losses,
          nTies: existing.nTies + s.count_ties,
          sortSlug: `${winPercentage.toFixed(5)}-${tiePercentage.toFixed(5)}-${s.other_model_name}`,
        },
      };
    }, {});
    return sortBy<ChartRecord>(prop('sortSlug'))(Object.values(statsEnhanced)).reverse();
  }, [headToHeadStats, judgeId]);

  function handleBarClick({ opponentId }: ChartRecord) {
    navigate(`/project/${projectSlug}/compare?modelA=${modelId}&modelB=${opponentId}`);
  }

  const isDisabled = plotStats.length == 0;
  return (
    <Paper p="xs" radius="md" withBorder>
      <Stack align="center" style={{ position: 'relative' }}>
        <Group justify="center" style={{ width: '100%', position: 'relative' }} flex={1}>
          <Title order={6} fw={500}>
            Record versus Opponents{judge != null ? ` as judged by '${judge.name}'` : ''}
          </Title>
          <Checkbox
            label={
              <Text c="dimmed" size="xs" fs="italic">
                Show as percentage
              </Text>
            }
            checked={isPercentage}
            onChange={() => setIsPercentage(prev => !prev)}
            style={{ position: 'absolute', right: 0 }}
            labelPosition="left"
          />
        </Group>
        <BarChart
          h={300}
          data={plotStats}
          dataKey="opponentName"
          type={isPercentage ? 'percent' : 'stacked'}
          cursorFill={isDisabled ? 'transparent' : undefined}
          tooltipAnimationDuration={200}
          barProps={{ onClick: handleBarClick }}
          series={[
            { name: 'nWins', label: '# Wins', color: 'green.3' },
            { name: 'nTies', label: '# Ties', color: 'gray.3' },
            { name: 'nLosses', label: '# Losses', color: 'red.3' },
          ]}
        />
        <LoadingOverlay visible={isLoading} overlayProps={{ radius: 'md', blur: 4 }} />
        <Box hidden={isLoading || !isDisabled} style={{ position: 'absolute', top: '25%' }}>
          <NonIdealState IconComponent={IconCactus} description="No records to display" />
        </Box>
      </Stack>
    </Paper>
  );
}
