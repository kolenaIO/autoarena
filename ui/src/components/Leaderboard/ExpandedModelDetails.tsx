import { Button, Group, Loader, Paper, Stack, Text } from '@mantine/core';
import { IconDownload, IconGavel, IconSwords } from '@tabler/icons-react';
import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import moment from 'moment/moment';
import { DeleteModelButton } from '../DeleteModelButton.tsx';
import {
  useModelHeadToHeadStatsByJudge,
  useUrlState,
  useTriggerModelAutoJudge,
  useDownloadFile,
  useAppRoutes,
} from '../../hooks';
import { RankedModel } from './types.ts';
import { HeadToHeadStatsTable } from './HeadToHeadStatsTable.tsx';
import { HeadToHeadStatsPlot } from './HeadToHeadStatsPlot.tsx';

type Props = {
  model: RankedModel;
};
export function ExpandedModelDetails({ model }: Props) {
  const { projectSlug = '', judgeId } = useUrlState();
  const { apiRoutes, appRoutes } = useAppRoutes();
  const { data: headToHeadStats, isLoading } = useModelHeadToHeadStatsByJudge({
    projectSlug,
    modelId: model.id,
    judgeId,
  });
  const { mutate: triggerModelJudgement } = useTriggerModelAutoJudge({ projectSlug, modelId: model.id });
  const { mutate: downloadResponses, isPending: isDownloadingResponses } = useDownloadFile(
    apiRoutes.downloadModelResponsesCsv(projectSlug, model.id),
    `${model.name}.csv`
  );
  const { mutate: downloadHeadToHeads, isPending: isDownloadingHeadToHeads } = useDownloadFile(
    apiRoutes.downloadModelHeadToHeadsCsv(projectSlug, model.id),
    `${model.name}-head-to-heads.csv`
  );

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
      <Paper p="xs" withBorder>
        <Stack gap="xs">
          <Group gap="xs" fz="xs" justify="space-between">
            <Group gap="xs">
              <Text inherit fw="bold">
                Record (Win - Loss - Tie):
              </Text>
              <Text inherit>
                {!isLoading && `${nWins.toLocaleString()} - ${nLosses.toLocaleString()} - ${nTies.toLocaleString()}`}
              </Text>
            </Group>
            <Group gap="xs">
              <Text inherit fw="bold">
                Created:
              </Text>
              <Text inherit>{moment(model.created).format('YYYY-MM-DD (hh:mm A)')}</Text>
            </Group>
          </Group>
          <Group gap="xs" justify="space-between" w="100%">
            <Group gap="xs">
              <Link to={`${appRoutes.compare(projectSlug)}?modelA=${model.id}`}>
                <Button color="cyan" variant="light" size="xs" leftSection={<IconSwords size={20} />}>
                  View Responses
                </Button>
              </Link>
              <Button
                color="teal"
                variant="light"
                size="xs"
                leftSection={isDownloadingResponses ? <Loader color="teal" size={20} /> : <IconDownload size={20} />}
                onClick={() => downloadResponses()}
              >
                Download Responses CSV
              </Button>
              <Button
                color="teal"
                variant="light"
                size="xs"
                leftSection={isDownloadingHeadToHeads ? <Loader color="teal" size={20} /> : <IconDownload size={20} />}
                onClick={() => downloadHeadToHeads()}
              >
                Download Head-to-Heads CSV
              </Button>
              <Button
                variant="light"
                color="orange"
                size="xs"
                leftSection={<IconGavel size={20} />}
                onClick={() => triggerModelJudgement()}
              >
                Run Automated Judgement
              </Button>
            </Group>
            <DeleteModelButton model={model} />
          </Group>
        </Stack>
      </Paper>

      <HeadToHeadStatsPlot modelId={model.id} />
      <HeadToHeadStatsTable modelId={model.id} />
    </Stack>
  );
}
