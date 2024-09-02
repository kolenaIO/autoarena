import { Stack } from '@mantine/core';
import { ReactNode } from 'react';

type Props = {
  children: ReactNode;
};
export function ControlBar({ children }: Props) {
  return (
    <Stack
      bg="gray.0"
      p="md"
      style={{ position: 'fixed', bottom: 0, left: 0, right: 0, borderTop: '1px solid var(--mantine-color-gray-3)' }}
    >
      {children}
    </Stack>
  );
}
