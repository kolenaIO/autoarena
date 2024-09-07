import { Group, Text, Tooltip } from '@mantine/core';
import { IconCrown } from '@tabler/icons-react';
import { RankedModel } from '../types.ts';

export function ModelNameRenderer({ name, votes, rank }: RankedModel) {
  return (
    <Group align="center" miw={250}>
      {votes > 0 ? (
        <Text size="md">{name}</Text>
      ) : (
        <Tooltip openDelay={200} label="No votes yet">
          <Text size="md" c="dimmed" fs="italic">
            {name}
          </Text>
        </Tooltip>
      )}
      {rank === 1 && votes > 0 && (
        <Tooltip openDelay={200} label="Champion">
          <IconCrown size={18} color="var(--mantine-color-yellow-6)" />
        </Tooltip>
      )}
    </Group>
  );
}
