import { IconArrowLeft, IconArrowRight, IconCactus } from '@tabler/icons-react';
import { Button, Group, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import { useMemo, useState } from 'react';
import { useHotkeys } from '@mantine/hooks';
import { pluralize } from '../../lib/string.ts';
import { useModelResponses } from '../../hooks/useModelResponses.ts';
import { NonIdealState } from '../NonIdealState.tsx';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { ControlBar } from './ControlBar.tsx';

type Props = {
  modelId: number;
};
export function HeadToHeadSingleModel({ modelId }: Props) {
  const { projectSlug } = useUrlState();
  const { data: modelResponses, isLoading } = useModelResponses({ projectSlug, modelId });
  const [responseIndex, setResponseIndex] = useState(0);

  const response = useMemo(() => (modelResponses ?? [])?.[responseIndex], [modelResponses, responseIndex]);
  const nResponses = useMemo(() => (modelResponses ?? []).length, [modelResponses]);

  function navigatePrevious() {
    setResponseIndex(prev => Math.max(0, prev - 1));
  }
  function navigateNext() {
    setResponseIndex(prev => Math.min(prev + 1, nResponses - 1));
  }

  useHotkeys([
    ['ArrowLeft', navigatePrevious],
    ['ArrowRight', navigateNext],
  ]);

  const iconProps = { size: 18 };
  return !isLoading && nResponses === 0 ? (
    <NonIdealState IconComponent={IconCactus} description="No responses from selected model" />
  ) : !isLoading ? (
    <>
      <Stack pb={100}>
        <Group justify="flex-end">
          <Text c="dimmed" size="sm" fs="italic">
            {pluralize(nResponses, 'response')} from selected model
          </Text>
        </Group>
        <Paper withBorder p="md" bg="gray.0" style={{ overflow: 'auto' }}>
          <MarkdownContent>{`**Prompt:** ${response?.prompt}`}</MarkdownContent>
        </Paper>
        <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
          <MarkdownContent>{`**Response:**\n\n${response?.response}`}</MarkdownContent>
        </Paper>
      </Stack>

      <ControlBar>
        <Stack align="center" gap="xs">
          <SimpleGrid cols={2} spacing="xs">
            <Button
              leftSection={<IconArrowLeft {...iconProps} />}
              onClick={navigatePrevious}
              disabled={responseIndex < 1}
            >
              Previous
            </Button>
            <Button
              rightSection={<IconArrowRight {...iconProps} />}
              onClick={navigateNext}
              disabled={responseIndex >= nResponses - 1}
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
