import { IconSparkles, TablerIcon } from '@tabler/icons-react';
import { Stack, Text } from '@mantine/core';
import { ReactNode } from 'react';

type Props = {
  IconComponent?: TablerIcon;
  icon?: ReactNode;
  description: string;
};
export function NonIdealState({ IconComponent = IconSparkles, icon, description }: Props) {
  return (
    <Stack align="center" p="xl">
      {icon ?? <IconComponent size={64} color="var(--mantine-color-kolena-8)" />}
      <Text c="dimmed">{description}</Text>
    </Stack>
  );
}
