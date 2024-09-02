import { Box, Button, Group, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import { IconArrowDown, IconArrowLeft, IconArrowRight, IconBalloon, IconCactus } from '@tabler/icons-react';
import { useEffect, useMemo, useState } from 'react';
import { useDisclosure, useHotkeys } from '@mantine/hooks';
import { useNavigate } from 'react-router-dom';
import { useHeadToHeads } from '../../hooks/useHeadToHeads.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useSubmitHeadToHeadJudgement } from '../../hooks/useSubmitHeadToHeadJudgement.ts';
import { pluralize } from '../../lib/string.ts';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { NonIdealState } from '../NonIdealState.tsx';
import { ControlBar } from './ControlBar.tsx';

type Props = {
  modelAId: number;
  modelBId: number;
};
export function HeadToHeadBattle({ modelAId, modelBId }: Props) {
  const { projectId = -1 } = useUrlState();
  const navigate = useNavigate();
  const [showJudgingHistory, { toggle: toggleShowJudgingHistory }] = useDisclosure(false);
  // TODO: loading state?
  const { data: battles, isLoading } = useHeadToHeads({ modelAId, modelBId });
  const { mutate: submitJudgement } = useSubmitHeadToHeadJudgement({ projectId });
  const [battleIndex, setBattleIndex] = useState(0);
  const battle = useMemo(() => battles?.[battleIndex], [battles, battleIndex]);
  const nBattles: number = battles?.length ?? 0;

  useEffect(() => {
    setBattleIndex(0);
  }, [modelAId, modelBId]);

  function navigatePrevious() {
    setBattleIndex(prev => Math.max(0, prev - 1));
  }
  function navigateNext() {
    setBattleIndex(prev => Math.min(prev + 1, nBattles - 1));
  }

  function submitVote(vote: 'A' | 'B' | '-') {
    return () => {
      if (battle != null) {
        submitJudgement({
          project_id: projectId,
          result_a_id: battle.result_a_id,
          result_b_id: battle.result_b_id,
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

  const hasJudgingHistory = (battle?.history?.length ?? 0) > 0;
  const { votesA, votesTie, votesB } = useMemo(() => {
    return (battle?.history ?? []).reduce<{ votesA: string[]; votesTie: string[]; votesB: string[] }>(
      ({ votesA, votesTie, votesB }, { winner, judge_name }) => ({
        votesA: [...votesA, ...(winner === 'A' ? [judge_name] : [])],
        votesTie: [...votesTie, ...(winner === '-' ? [judge_name] : [])],
        votesB: [...votesB, ...(winner === 'B' ? [judge_name] : [])],
      }),
      { votesA: [], votesTie: [], votesB: [] }
    );
  }, [showJudgingHistory, battle]);

  const iconProps = { size: 18 };
  return !isLoading && nBattles === 0 ? (
    <NonIdealState IconComponent={IconCactus} description="No head-to-head matchups between selected models" />
  ) : !isLoading && battleIndex > nBattles - 1 ? (
    <NonIdealState
      IconComponent={IconBalloon}
      description={
        <Stack>
          <Text>Judged all {nBattles.toLocaleString()} head-to-head matchups between selected models</Text>
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
        <Paper withBorder p="md" bg="gray.0" style={{ overflow: 'auto' }}>
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

      <ControlBar>
        <Stack align="center" gap="xs">
          <Text fw="bold">Which response is better?</Text>
          <SimpleGrid cols={5} spacing="xs">
            <Button variant="subtle" color="gray" onClick={navigatePrevious}>
              Previous
            </Button>
            <Button leftSection={<IconArrowLeft {...iconProps} />} onClick={submitVote('A')}>
              Left
            </Button>
            <Button leftSection={<IconArrowDown {...iconProps} />} onClick={submitVote('-')}>
              Tie
            </Button>
            <Button rightSection={<IconArrowRight {...iconProps} />} onClick={submitVote('B')}>
              Right
            </Button>
            <Button variant="subtle" color="gray" onClick={navigateNext}>
              Next
            </Button>
            {showJudgingHistory && (
              <>
                <div />
                {[votesA, votesTie, votesB].map((votes, i) => (
                  <Stack key={i} gap="xs" align="center" fz="xs">
                    {votes.map((judge, i) => (
                      <Text key={i} span inherit>
                        {judge}
                      </Text>
                    ))}
                  </Stack>
                ))}
                <div />
              </>
            )}
          </SimpleGrid>
        </Stack>

        <Box p="md" style={{ position: 'fixed', bottom: 0, right: 0 }}>
          <Button
            variant="subtle"
            color="gray"
            size="xs"
            onClick={toggleShowJudgingHistory}
            disabled={!hasJudgingHistory}
          >
            {!hasJudgingHistory ? 'No' : showJudgingHistory ? 'Hide' : 'Show'} Judging History
          </Button>
        </Box>
      </ControlBar>
    </>
  ) : (
    <></>
  );
}
