import { TablerIcon } from '@tabler/icons-react';
import { Stack, Text } from '@mantine/core';

type Props = {
  IconComponent: TablerIcon;
  description: string;
};
export function NonIdealState({ IconComponent, description }: Props) {
  return (
    <Stack align="center" p="xl">
      <IconComponent size={64} color="var(--mantine-color-kolena-8)" />
      <Text c="dimmed">{description}</Text>
    </Stack>
  );
}
