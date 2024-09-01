import { Group, Stack } from '@mantine/core';
import { DeleteModelButton } from '../DeleteModelButton.tsx';
import { RankedModel } from './types.ts';

type Props = {
  model: RankedModel;
};
export function ExpandedModelDetails({ model }: Props) {
  return (
    <Stack bg="gray.1" p="sm">
      <Group justify="space-between">
        <div>foobar</div>
        <DeleteModelButton model={model} />
      </Group>
    </Stack>
  );
}
