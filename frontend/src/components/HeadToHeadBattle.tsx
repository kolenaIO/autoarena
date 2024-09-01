import { Box, Button, Group, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import { IconArrowDown, IconArrowLeft, IconArrowRight, IconBalloon, IconCactus } from '@tabler/icons-react';
import { Fragment, useEffect, useMemo, useState } from 'react';
import { useDisclosure, useHotkeys } from '@mantine/hooks';
import { useNavigate } from 'react-router-dom';
import { useHeadToHeads } from '../hooks/useHeadToHeads.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useSubmitHeadToHeadJudgement } from '../hooks/useSubmitHeadToHeadJudgement.ts';
import { pluralize } from '../lib/string.ts';
import { MarkdownContent } from './MarkdownContent.tsx';
import { NonIdealState } from './NonIdealState.tsx';

type Props = {
  modelAId: number;
  modelBId: number;
};
export function HeadToHeadBattle({ modelAId, modelBId }: Props) {
  const { projectId = -1 } = useUrlState();
  const navigate = useNavigate();
  const [showJudgingHistory, { toggle: toggleShowJudgingHistory }] = useDisclosure(false);
  // TODO: loading state?
  const { data: battles, isLoading } = useHeadToHeads({ projectId, modelAId, modelBId });
  const { mutate: submitJudgement } = useSubmitHeadToHeadJudgement({ projectId });
  const [battleIndex, setBattleIndex] = useState(0);
  const battle = useMemo(() => battles?.[battleIndex], [battles, battleIndex]);

  useEffect(() => {
    setBattleIndex(0);
  }, [modelAId, modelBId]);

  function submitVote(vote: 'A' | 'B' | '-') {
    return () => {
      if (battle != null) {
        submitJudgement({
          project_id: projectId,
          result_a_id: battle?.result_a_id,
          result_b_id: battle?.result_b_id,
          winner: vote,
        });
        setBattleIndex(prev => prev + 1);
      }
    };
  }

  useHotkeys([
    ['ArrowLeft', submitVote('A')],
    ['ArrowDown', submitVote('-')],
    ['ArrowRight', submitVote('B')],
  ]);

  const nBattles: number = battles?.length ?? 0;
  const iconProps = { size: 18 };
  return !isLoading && nBattles === 0 ? (
    <NonIdealState IconComponent={IconCactus} description="No head-to-head battles between selected models" />
  ) : !isLoading && battleIndex > nBattles - 1 ? (
    <NonIdealState
      IconComponent={IconBalloon}
      description={
        <Stack>
          <Text>Judged all {nBattles.toLocaleString()} head-to-head battles between selected models</Text>
          <Button onClick={() => navigate(`/project/${projectId}`)}>View Leaderboard</Button>
        </Stack>
      }
    />
  ) : !isLoading ? (
    <>
      <Stack pb={100}>
        <Group justify="flex-end">
          <Text c="dimmed" size="sm" fs="italic">
            {pluralize(nBattles, 'head-to-head battle')} between selected models
          </Text>
        </Group>
        <Paper withBorder p="md">
          <MarkdownContent>{`**Prompt:** ${battle?.prompt}`}</MarkdownContent>
        </Paper>
        <SimpleGrid cols={2}>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response A:**\n\n${battle?.response_a}`}</MarkdownContent>
          </Paper>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response B:**\n\n${battle?.response_b}`}</MarkdownContent>
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
            <Button leftSection={<IconArrowLeft {...iconProps} />} onClick={submitVote('A')}>
              Left
            </Button>
            <Button leftSection={<IconArrowDown {...iconProps} />} onClick={submitVote('-')}>
              Tie
            </Button>
            <Button rightSection={<IconArrowRight {...iconProps} />} onClick={submitVote('B')}>
              Right
            </Button>
            {showJudgingHistory &&
              battle?.history?.map((item, i) => (
                <Fragment key={i}>
                  <Text ta="center" size="xs">
                    {item.winner === 'A' && item.judge_name}
                  </Text>
                  <Text ta="center" size="xs">
                    {item.winner === '-' && item.judge_name}
                  </Text>
                  <Text ta="center" size="xs">
                    {item.winner === 'B' && item.judge_name}
                  </Text>
                </Fragment>
              ))}
          </SimpleGrid>
        </Stack>

        <Box p="md" style={{ position: 'fixed', bottom: 0, right: 0 }}>
          <Button variant="subtle" color="gray" size="xs" onClick={toggleShowJudgingHistory}>
            {showJudgingHistory ? 'Hide' : 'Show'} Judging History
          </Button>
        </Box>
      </Stack>
    </>
  ) : (
    <></>
  );
}
