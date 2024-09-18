import { Anchor, Button, Group, Skeleton, Stack, Text } from '@mantine/core';
import moment from 'moment';
import { IconDownload, IconSwords } from '@tabler/icons-react';
import { useMemo } from 'react';
import { DeleteModelButton } from '../DeleteModelButton.tsx';
import { API_ROUTES, ROUTES } from '../../lib/routes.ts';
import { useModelHeadToHeadStatsByJudge } from '../../hooks/useModelHeadToHeadStatsByJudge.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { RankedModel } from './types.ts';
import { HeadToHeadStatsTable } from './HeadToHeadStatsTable.tsx';
import { HeadToHeadStatsPlot } from './HeadToHeadStatsPlot.tsx';

type Props = {
  model: RankedModel;
};
export function ExpandedModelDetails({ model }: Props) {
  const { projectSlug = '', judgeId } = useUrlState();
  const { data: headToHeadStats, isLoading } = useModelHeadToHeadStatsByJudge({
    projectSlug,
    modelId: model.id,
    judgeId,
  });

  const { nWins, nTies, nLosses } = useMemo(
    () => ({
      nWins: (headToHeadStats ?? []).reduce((acc, { count_wins: ct }) => acc + ct, 0),
      nTies: (headToHeadStats ?? []).reduce((acc, { count_ties: ct }) => acc + ct, 0),
      nLosses: (headToHeadStats ?? []).reduce((acc, { count_losses: ct }) => acc + ct, 0),
    }),
    [headToHeadStats]
  );

  return (
    <Stack bg="gray.1" gap="xs" pt="xs" p="xl">
      <Group justify="space-between">
        <Stack gap={2} fz="xs">
          <Group gap="xs">
            <Text inherit fw="bold">
              Created:
            </Text>
            <Text inherit>{moment(model.created).format('YYYY-MM-DD (hh:mm A)')}</Text>
          </Group>
          <Group gap="xs">
            <Text inherit fw="bold">
              Record (Win - Loss - Tie):
            </Text>
            <Text inherit>
              <Skeleton visible={isLoading}>
                {nWins.toLocaleString()} - {nLosses.toLocaleString()} - {nTies.toLocaleString()}
              </Skeleton>
            </Text>
          </Group>
        </Stack>
        <Group gap="xs">
          <Anchor href={`${ROUTES.compare(projectSlug)}?modelA=${model.id}`}>
            <Button color="cyan" variant="light" size="xs" leftSection={<IconSwords size={20} />}>
              View Responses
            </Button>
          </Anchor>
          <Anchor href={API_ROUTES.downloadModelResponsesCsv(projectSlug, model.id)} target="_blank">
            <Button color="teal" variant="light" size="xs" leftSection={<IconDownload size={20} />}>
              Download Response CSV
            </Button>
          </Anchor>
          <Anchor href={API_ROUTES.downloadModelHeadToHeadsCsv(projectSlug, model.id)} target="_blank">
            <Button color="teal" variant="light" size="xs" leftSection={<IconDownload size={20} />}>
              Download Head-to-Head CSV
            </Button>
          </Anchor>
          <DeleteModelButton model={model} />
        </Group>
      </Group>
      <HeadToHeadStatsPlot modelId={model.id} />
      <HeadToHeadStatsTable modelId={model.id} />
    </Stack>
  );
}
