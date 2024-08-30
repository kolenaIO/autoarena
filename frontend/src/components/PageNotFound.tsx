import { Button, Stack, Title } from '@mantine/core';
import { IconError404 } from '@tabler/icons-react';
import { useRouteError } from 'react-router-dom';

export function PageNotFound() {
  useRouteError();
  return (
    <Stack justify="center" align="center" h="100vh">
      <Stack justify="center" align="center">
        <Title order={2}>Page Not Found</Title>
        <IconError404 size={32} />
        <Button onClick={() => (window.location.href = '/')}>Return Home</Button>
      </Stack>
    </Stack>
  );
}
