import { Anchor, Button, Group, Stack, Text } from '@mantine/core';
import moment from 'moment';
import { IconDownload } from '@tabler/icons-react';
import { DeleteModelButton } from '../DeleteModelButton.tsx';
import { BASE_API_URL } from '../paths.ts';
import { RankedModel } from './types.ts';
import { HeadToHeadStatsTable } from './HeadToHeadStatsTable.tsx';
import { EloHistoryPlot } from './EloHistoryPlot.tsx';

type Props = {
  model: RankedModel;
};
export function ExpandedModelDetails({ model }: Props) {
  return (
    <Stack bg="gray.1" gap="xs" pt="xs" p="xl">
      <Group justify="space-between">
        <Group gap="xs">
          <Text span fw="bold">
            Created:
          </Text>
          <Text span>{moment(model.created).format('YYYY-MM-DD (hh:mm A)')}</Text>
        </Group>
        <Group>
          <Anchor href={`${BASE_API_URL}/model/${model.id}/download/results`} target="_blank">
            <Button color="teal" variant="light" leftSection={<IconDownload />}>
              Download Results CSV
            </Button>
          </Anchor>
          <Anchor href={`${BASE_API_URL}/model/${model.id}/download/head-to-heads`} target="_blank">
            <Button color="teal" variant="light" leftSection={<IconDownload />}>
              Download Head-to-Heads CSV
            </Button>
          </Anchor>
          <DeleteModelButton model={model} />
        </Group>
      </Group>
      <EloHistoryPlot modelId={model.id} />
      <HeadToHeadStatsTable modelId={model.id} />
    </Stack>
  );
}
