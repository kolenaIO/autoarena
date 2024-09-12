import { Group, Text, Tooltip } from '@mantine/core';
import { IconCrown } from '@tabler/icons-react';
import { RankedModel } from '../types.ts';

export function ModelNameRenderer({ name, n_votes, rank }: RankedModel) {
  return (
    <Group align="center" wrap="nowrap">
      {n_votes > 0 ? (
        <Text size="md">{name}</Text>
      ) : (
        <Tooltip label="No votes yet">
          <Text size="md" c="dimmed" fs="italic">
            {name}
          </Text>
        </Tooltip>
      )}
      {rank === 1 && n_votes > 0 && (
        <Tooltip label="Champion">
          <IconCrown size={18} color="var(--mantine-color-yellow-6)" style={{ flexShrink: 0 }} />
        </Tooltip>
      )}
    </Group>
  );
}
