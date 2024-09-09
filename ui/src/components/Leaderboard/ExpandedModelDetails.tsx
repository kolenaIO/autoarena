import { Anchor, Button, Group, Skeleton, Stack, Text } from '@mantine/core';
import moment from 'moment';
import { IconDownload, IconGavel } from '@tabler/icons-react';
import { useMemo } from 'react';
import { DeleteModelButton } from '../DeleteModelButton.tsx';
import { getProjectUrl } from '../../lib/routes.ts';
import { useModelHeadToHeadStatsByJudge } from '../../hooks/useModelHeadToHeadStatsByJudge.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useTriggerModelJudgement } from '../../hooks/useTriggerModelJudgement.ts';
import { RankedModel } from './types.ts';
import { HeadToHeadStatsTable } from './HeadToHeadStatsTable.tsx';
import { EloHistoryPlot } from './EloHistoryPlot.tsx';

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
  const { mutate: triggerModelJudgement } = useTriggerModelJudgement({ projectSlug, modelId: model.id });

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
          <Anchor href={`${getProjectUrl(projectSlug)}/model/${model.id}/download/responses`} target="_blank">
            <Button color="teal" variant="light" size="xs" leftSection={<IconDownload size={20} />}>
              Download Responses CSV
            </Button>
          </Anchor>
          <Anchor href={`${getProjectUrl(projectSlug)}/model/${model.id}/download/head-to-heads`} target="_blank">
            <Button color="teal" variant="light" size="xs" leftSection={<IconDownload size={20} />}>
              Download Head-to-Heads CSV
            </Button>
          </Anchor>
          <Button
            variant="light"
            color="orange"
            size="xs"
            leftSection={<IconGavel size={20} />}
            onClick={() => triggerModelJudgement()}
          >
            Run Automated Judgement
          </Button>
          <DeleteModelButton model={model} />
        </Group>
      </Group>
      <EloHistoryPlot modelId={model.id} />
      <HeadToHeadStatsTable modelId={model.id} />
    </Stack>
  );
}
