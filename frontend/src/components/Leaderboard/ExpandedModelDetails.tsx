import { Anchor, Button, Group, Stack, Text } from '@mantine/core';
import moment from 'moment';
import { IconDownload } from '@tabler/icons-react';
import { DeleteModelButton } from '../DeleteModelButton.tsx';
import { BASE_API_URL } from '../paths.ts';
import { RankedModel } from './types.ts';

type Props = {
  model: RankedModel;
};
export function ExpandedModelDetails({ model }: Props) {
  return (
    <Stack bg="gray.1" p="sm">
      <Group justify="space-between">
        <Group gap="xs">
          <Text span fw="bold">
            Created:
          </Text>
          <Text span>{moment(model.created).format('YYYY-MM-DD (hh:mm A)')}</Text>
        </Group>
        <Group>
          <Anchor href={`${BASE_API_URL}/model/${model.id}/results`} target="_blank">
            <Button color="teal" variant="light" leftSection={<IconDownload />}>
              Download Results CSV
            </Button>
          </Anchor>
          <Anchor href={`${BASE_API_URL}/model/${model.id}/head-to-heads`} target="_blank">
            <Button color="teal" variant="light" leftSection={<IconDownload />}>
              Download Head-to-Heads CSV
            </Button>
          </Anchor>
          <DeleteModelButton model={model} />
        </Group>
      </Group>
    </Stack>
  );
}
