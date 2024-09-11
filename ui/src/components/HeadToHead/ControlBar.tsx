import { Stack } from '@mantine/core';
import { forwardRef, ReactNode } from 'react';

type Props = {
  children: ReactNode;
};
export const ControlBar = forwardRef<HTMLDivElement, Props>(function ControlBar({ children }, ref) {
  return (
    <Stack
      ref={ref}
      bg="gray.0"
      p="md"
      style={{ position: 'fixed', bottom: 0, left: 0, right: 0, borderTop: '1px solid var(--mantine-color-gray-3)' }}
    >
      {children}
    </Stack>
  );
});
