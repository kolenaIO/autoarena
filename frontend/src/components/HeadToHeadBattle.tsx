import { Button, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import { IconArrowLeft, IconArrowRight, IconBalloon, IconCactus, IconHeartHandshake } from '@tabler/icons-react';
import { useEffect, useMemo, useState } from 'react';
import { useHotkeys } from '@mantine/hooks';
import { useHeadToHeadBattles } from './useHeadToHeadBattles.ts';
import { MarkdownContent } from './MarkdownContent.tsx';

type Props = {
  modelAId: number;
  modelBId: number;
};
export function HeadToHeadBattle({ modelAId, modelBId }: Props) {
  // TODO: loading state?
  const { data: battles, isLoading } = useHeadToHeadBattles({ modelAId, modelBId });
  const [battleIndex, setBattleIndex] = useState(0);
  const battle = useMemo(() => battles?.[battleIndex], [battles, battleIndex]);

  useEffect(() => {
    setBattleIndex(0);
  }, [modelAId, modelBId]);

  function submitVote(vote: 'A' | 'B' | 'neither') {
    return () => {
      console.log(`vote: ${vote} (index: ${battleIndex})`);
      setBattleIndex(prev => prev + 1);
    };
  }

  useHotkeys([
    ['ArrowLeft', submitVote('A')],
    ['Space', submitVote('neither')],
    ['ArrowRight', submitVote('B')],
  ]);

  const nBattles = battles?.length ?? 0;
  const iconProps = { size: 18 };
  return !isLoading && nBattles === 0 ? (
    <Stack align="center" p="xl">
      <IconCactus size={64} color="var(--mantine-color-kolena-8)" />
      <Text c="dimmed">No head-to-head battles between selected models</Text>
    </Stack>
  ) : battleIndex > nBattles - 1 ? (
    <Stack align="center" p="xl">
      <IconBalloon size={64} color="var(--mantine-color-kolena-8)" />
      <Text c="dimmed">Voted on all {nBattles.toLocaleString()} head-to-head battles between selected models</Text>
    </Stack>
  ) : (
    <>
      <Stack pb={100}>
        <Text c="dimmed" size="sm" fs="italic">
          Showing {nBattles} head-to-head battle{nBattles > 1 && 's'} between selected models
        </Text>
        <Paper withBorder p="md">
          <MarkdownContent>{`**Prompt:** ${battle?.prompt}`}</MarkdownContent>
        </Paper>
        <SimpleGrid cols={2}>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response A:** ${battle?.response_a}`}</MarkdownContent>
          </Paper>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response B:** ${battle?.response_b}`}</MarkdownContent>
          </Paper>
        </SimpleGrid>
      </Stack>
      <Stack
        bg="gray.0"
        p="md"
        style={{ position: 'fixed', bottom: 0, left: 0, right: 0, borderTop: '1px solid var(--mantine-color-gray-3)' }}
      >
        <Stack align="center" gap="xs">
          <Text fw="bold">Which response is better?</Text>
          <SimpleGrid cols={3} spacing="xs">
            <Button leftSection={<IconArrowLeft {...iconProps} />}>Left</Button>
            <Button leftSection={<IconHeartHandshake {...iconProps} />}>Tie</Button>
            <Button rightSection={<IconArrowRight {...iconProps} />}>Right</Button>
          </SimpleGrid>
        </Stack>
      </Stack>
    </>
  );
}
