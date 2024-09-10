import { Box, Button, Group, Kbd, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import {
  IconArrowDown,
  IconArrowLeft,
  IconArrowRight,
  IconArrowUp,
  IconBalloon,
  IconCactus,
} from '@tabler/icons-react';
import { useEffect, useMemo, useState } from 'react';
import { useDisclosure, useHotkeys } from '@mantine/hooks';
import { useNavigate } from 'react-router-dom';
import { useHeadToHeads } from '../../hooks/useHeadToHeads.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useSubmitHeadToHeadVote } from '../../hooks/useSubmitHeadToHeadVote.ts';
import { pluralize } from '../../lib/string.ts';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { NonIdealState } from '../NonIdealState.tsx';
import { ControlBar } from './ControlBar.tsx';

type Props = {
  modelAId: number;
  modelBId: number;
};
export function HeadToHeadTwoModels({ modelAId, modelBId }: Props) {
  const { projectSlug = '' } = useUrlState();
  const navigate = useNavigate();
  const [showJudgingHistory, { toggle: toggleShowJudgingHistory }] = useDisclosure(false);
  // TODO: loading state?
  const { data: battles, isLoading } = useHeadToHeads({ projectSlug, modelAId, modelBId });
  const { mutate: submitJudgement } = useSubmitHeadToHeadVote({ projectSlug });
  const [headToHeadIndex, setHeadToHeadIndex] = useState(0);
  const headToHead = useMemo(() => battles?.[headToHeadIndex], [battles, headToHeadIndex]);
  const nHeadToHeads: number = battles?.length ?? 0;

  useEffect(() => {
    setHeadToHeadIndex(0);
  }, [modelAId, modelBId]);

  function navigatePrevious() {
    setHeadToHeadIndex(prev => Math.max(0, prev - 1));
  }
  function navigateNext() {
    setHeadToHeadIndex(prev => Math.min(prev + 1, nHeadToHeads - 1));
  }

  function submitVote(vote: 'A' | 'B' | '-') {
    return () => {
      if (headToHead != null) {
        submitJudgement({
          response_a_id: headToHead.response_a_id,
          response_b_id: headToHead.response_b_id,
          winner: vote,
        });
        setHeadToHeadIndex(prev => prev + 1);
      }
    };
  }

  useHotkeys([
    ['ArrowLeft', submitVote('A')],
    ['ArrowUp', submitVote('-')],
    ['ArrowDown', submitVote('-')],
    ['ArrowRight', submitVote('B')],
    ['p', navigatePrevious],
    ['n', navigateNext],
    ['j', toggleShowJudgingHistory],
  ]);

  const hasJudgingHistory = (headToHead?.history?.length ?? 0) > 0;
  const { votesA, votesTie, votesB } = useMemo(() => {
    return (headToHead?.history ?? []).reduce<{ votesA: string[]; votesTie: string[]; votesB: string[] }>(
      ({ votesA, votesTie, votesB }, { winner, judge_name }) => ({
        votesA: [...votesA, ...(winner === 'A' ? [judge_name] : [])],
        votesTie: [...votesTie, ...(winner === '-' ? [judge_name] : [])],
        votesB: [...votesB, ...(winner === 'B' ? [judge_name] : [])],
      }),
      { votesA: [], votesTie: [], votesB: [] }
    );
  }, [showJudgingHistory, headToHead]);

  const iconProps = { size: 18 };
  return !isLoading && nHeadToHeads === 0 ? (
    <NonIdealState IconComponent={IconCactus} description="No head-to-head matchups between selected models" />
  ) : !isLoading && headToHeadIndex > nHeadToHeads - 1 ? (
    <NonIdealState
      IconComponent={IconBalloon}
      description={
        <Stack>
          <Text>Judged all {nHeadToHeads.toLocaleString()} head-to-head matchups between selected models</Text>
          <Button onClick={() => navigate(`/project/${projectSlug}`)}>View Leaderboard</Button>
        </Stack>
      }
    />
  ) : !isLoading ? (
    <>
      <Stack pb={100} /* TODO: need more padding when there are more judge responses shown */>
        <Group justify="flex-end">
          <Text c="dimmed" size="sm" fs="italic">
            {pluralize(nHeadToHeads, 'head-to-head')} between selected models
          </Text>
        </Group>
        <Paper withBorder p="md" bg="gray.0" style={{ overflow: 'auto' }}>
          <MarkdownContent>{`**Prompt:** ${headToHead?.prompt}`}</MarkdownContent>
        </Paper>
        <SimpleGrid cols={2}>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response A:**\n\n${headToHead?.response_a}`}</MarkdownContent>
          </Paper>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response B:**\n\n${headToHead?.response_b}`}</MarkdownContent>
          </Paper>
        </SimpleGrid>
      </Stack>

      <ControlBar>
        <Stack align="center" gap="xs">
          <Text fw="bold">Which response is better?</Text>
          <SimpleGrid cols={5} spacing="xs">
            <Button
              leftSection={<Kbd>p</Kbd>}
              variant="subtle"
              color="gray"
              onClick={navigatePrevious}
              disabled={headToHeadIndex < 1}
              h="100%"
            >
              Previous
            </Button>
            <Button leftSection={<IconArrowLeft {...iconProps} />} onClick={submitVote('A')} h="100%">
              Left is Better
            </Button>
            <Stack gap={4}>
              <Button size="compact-xs" leftSection={<IconArrowUp {...iconProps} />} onClick={submitVote('-')}>
                Both are Good
              </Button>
              <Button size="compact-xs" leftSection={<IconArrowDown {...iconProps} />} onClick={submitVote('-')}>
                Both are Bad
              </Button>
            </Stack>
            <Button rightSection={<IconArrowRight {...iconProps} />} onClick={submitVote('B')} h="100%">
              Right is Better
            </Button>
            <Button
              rightSection={<Kbd>n</Kbd>}
              variant="subtle"
              color="gray"
              onClick={navigateNext}
              disabled={headToHeadIndex >= nHeadToHeads - 1}
              h="100%"
            >
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
            rightSection={<Kbd size="xs">j</Kbd>}
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
