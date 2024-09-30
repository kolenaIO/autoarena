import { Button, Group, Paper, Stack, Text } from '@mantine/core';
import { IconExclamationCircle, IconHome, IconRefresh } from '@tabler/icons-react';
import { NonIdealState } from '../NonIdealState.tsx';

export function UnhandledError() {
  return (
    <Stack justify="center" align="center" h="100vh">
      <Paper withBorder p="xl">
        <NonIdealState
          IconComponent={IconExclamationCircle}
          description={
            <Stack align="center">
              <Text>Unhandled Application Error</Text>
              <Group>
                <Button
                  leftSection={<IconRefresh size={20} />}
                  variant="light"
                  color="kolena"
                  onClick={() => window.location.reload()}
                >
                  Refresh Page
                </Button>
                <Button
                  variant="light"
                  color="kolena"
                  leftSection={<IconHome size={20} />}
                  onClick={() => {
                    window.location.href = '/';
                  }}
                >
                  Return Home
                </Button>
              </Group>
            </Stack>
          }
        />
      </Paper>
    </Stack>
  );
}
