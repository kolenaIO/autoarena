import { IconArrowLeft, IconArrowRight, IconCactus } from '@tabler/icons-react';
import { Button, Group, Kbd, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import { useMemo, useState } from 'react';
import { useElementSize, useHotkeys } from '@mantine/hooks';
import { pluralize } from '../../lib';
import { NonIdealState } from '../NonIdealState.tsx';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { useUrlState, useModel, useModelResponses } from '../../hooks';
import { ControlBar } from './ControlBar.tsx';

type Props = {
  modelId: number;
};
export function HeadToHeadSingleModel({ modelId }: Props) {
  const { projectSlug } = useUrlState();
  const { data: model } = useModel(projectSlug, modelId);
  const { data: modelResponses, isLoading } = useModelResponses({ projectSlug, modelId });
  const [responseIndex, setResponseIndex] = useState(0);
  const { ref: controlBarRef, height } = useElementSize<HTMLDivElement>();

  const response = useMemo(() => (modelResponses ?? [])?.[responseIndex], [modelResponses, responseIndex]);
  const nResponses = useMemo(() => (modelResponses ?? []).length, [modelResponses]);

  function navigateBack() {
    setResponseIndex(prev => Math.max(0, prev - 1));
  }
  function navigateNext() {
    setResponseIndex(prev => Math.min(prev + 1, nResponses - 1));
  }

  useHotkeys([
    ['ArrowLeft', navigateBack],
    ['ArrowRight', navigateNext],
    ['b', navigateBack],
    ['n', navigateNext],
  ]);

  const modelName = model != null ? `'${model.name}'` : 'selected model';
  const iconProps = { size: 18 };
  return !isLoading && nResponses === 0 ? (
    <Paper withBorder p="xl" bg="white">
      <NonIdealState IconComponent={IconCactus} description={`No responses from ${modelName}`} />
    </Paper>
  ) : !isLoading ? (
    <>
      <Stack pb={height + 32}>
        <Group justify="flex-end">
          <Text c="dimmed" size="sm" fs="italic">
            {pluralize(nResponses, 'response')} from {modelName}
          </Text>
        </Group>
        <Paper withBorder p="md" bg="gray.0" style={{ overflow: 'auto' }}>
          <MarkdownContent>{`**Prompt:** ${response?.prompt}`}</MarkdownContent>
        </Paper>
        <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
          <MarkdownContent>{`**Response:**\n\n${response?.response}`}</MarkdownContent>
        </Paper>
      </Stack>

      <ControlBar ref={controlBarRef}>
        <Stack align="center" gap="xs">
          <SimpleGrid cols={2} spacing="xs">
            <Group justify="space-between">
              <Kbd>b</Kbd>
              <Button
                leftSection={<IconArrowLeft {...iconProps} />}
                onClick={navigateBack}
                disabled={responseIndex < 1}
                variant="light"
              >
                Back
              </Button>
            </Group>
            <Group justify="space-between">
              <Button
                rightSection={<IconArrowRight {...iconProps} />}
                onClick={navigateNext}
                disabled={responseIndex >= nResponses - 1}
                variant="light"
              >
                Next
              </Button>
              <Kbd>n</Kbd>
            </Group>
          </SimpleGrid>
        </Stack>
      </ControlBar>
    </>
  ) : (
    <></>
  );
}
