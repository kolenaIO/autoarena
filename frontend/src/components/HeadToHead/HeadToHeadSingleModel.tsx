import { IconArrowLeft, IconArrowRight, IconCactus } from '@tabler/icons-react';
import { Button, Group, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import { useMemo, useState } from 'react';
import { useHotkeys } from '@mantine/hooks';
import { pluralize } from '../../lib/string.ts';
import { useModelResults } from '../../hooks/useModelResults.ts';
import { NonIdealState } from '../NonIdealState.tsx';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { ControlBar } from './ControlBar.tsx';

type Props = {
  modelId: number;
};
export function HeadToHeadSingleModel({ modelId }: Props) {
  const { data: modelResults, isLoading } = useModelResults(modelId);
  const [resultIndex, setResultIndex] = useState(0);

  const result = useMemo(() => (modelResults ?? [])?.[resultIndex], [modelResults, resultIndex]);
  const nResults = useMemo(() => (modelResults ?? []).length, [modelResults]);

  function navigatePrevious() {
    setResultIndex(prev => Math.max(0, prev - 1));
  }
  function navigateNext() {
    setResultIndex(prev => Math.min(prev + 1, nResults - 1));
  }

  useHotkeys([
    ['ArrowLeft', navigatePrevious],
    ['ArrowRight', navigateNext],
  ]);

  const iconProps = { size: 18 };
  return !isLoading && nResults === 0 ? (
    <NonIdealState IconComponent={IconCactus} description="No results from selected model" />
  ) : !isLoading ? (
    <>
      <Stack pb={100}>
        <Group justify="flex-end">
          <Text c="dimmed" size="sm" fs="italic">
            {pluralize(nResults, 'result')} from selected model
          </Text>
        </Group>
        <Paper withBorder p="md" bg="gray.0">
          <MarkdownContent>{`**Prompt:** ${result?.prompt}`}</MarkdownContent>
        </Paper>
        <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
          <MarkdownContent>{`**Response:**\n\n${result?.response}`}</MarkdownContent>
        </Paper>
      </Stack>

      <ControlBar>
        <Stack align="center" gap="xs">
          <SimpleGrid cols={2} spacing="xs">
            <Button
              leftSection={<IconArrowLeft {...iconProps} />}
              onClick={navigatePrevious}
              disabled={resultIndex < 1}
            >
              Previous
            </Button>
            <Button
              rightSection={<IconArrowRight {...iconProps} />}
              onClick={navigateNext}
              disabled={resultIndex >= nResults - 1}
            >
              Next
            </Button>
          </SimpleGrid>
        </Stack>
      </ControlBar>
    </>
  ) : (
    <></>
  );
}
