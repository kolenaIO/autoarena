import { Button, Stack, Text } from '@mantine/core';
import { IconFileUnknown } from '@tabler/icons-react';
import { useRouteError } from 'react-router-dom';
import { NonIdealState } from './NonIdealState.tsx';

export function PageNotFound() {
  useRouteError();
  return (
    <Stack justify="center" align="center" h="100vh">
      <Stack justify="center" align="center">
        <NonIdealState
          IconComponent={IconFileUnknown}
          description={
            <Stack align="center">
              <Text>Page Not Found</Text>
              <Button onClick={() => (window.location.href = '/')}>Return Home</Button>
            </Stack>
          }
        />
      </Stack>
    </Stack>
  );
}
