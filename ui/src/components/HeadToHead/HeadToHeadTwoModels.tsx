import { Box, Button, Checkbox, Group, Kbd, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
import {
  IconArrowDown,
  IconArrowLeft,
  IconArrowRight,
  IconArrowUp,
  IconBalloon,
  IconCactus,
} from '@tabler/icons-react';
import { useEffect, useMemo, useState } from 'react';
import { useDisclosure, useElementSize, useHotkeys } from '@mantine/hooks';
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
  const [showVoteHistory, { toggle: toggleShowVoteHistory }] = useDisclosure(false);
  const { data: allHeadToHeads, isLoading } = useHeadToHeads({ projectSlug, modelAId, modelBId });
  const { mutate: submitJudgement } = useSubmitHeadToHeadVote({ projectSlug });
  const [headToHeadIndex, setHeadToHeadIndex] = useState(0);
  const { ref: controlBarRef, height } = useElementSize<HTMLDivElement>();
  const [showOnlyJudged, setShowOnlyJudged] = useState(false);

  const headToHeads = useMemo(
    () =>
      !showOnlyJudged ? (allHeadToHeads ?? []) : (allHeadToHeads ?? []).filter(({ history }) => history.length > 0),
    [allHeadToHeads, showOnlyJudged]
  );
  const headToHead = useMemo(() => headToHeads[headToHeadIndex], [headToHeads, headToHeadIndex]);
  const nHeadToHeadsTotal = (allHeadToHeads ?? []).length;
  const nHeadToHeads = headToHeads.length;

  useEffect(() => {
    setHeadToHeadIndex(0);
  }, [modelAId, modelBId]);

  function toggleShowOnlyJudged() {
    setHeadToHeadIndex(0);
    setShowOnlyJudged(prev => !prev);
  }
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
    ['h', toggleShowVoteHistory],
  ]);

  const hasVoteHistory = (headToHead?.history?.length ?? 0) > 0;
  const { votesA, votesTie, votesB } = useMemo(() => {
    return (headToHead?.history ?? []).reduce<{ votesA: string[]; votesTie: string[]; votesB: string[] }>(
      ({ votesA, votesTie, votesB }, { winner, judge_name }) => ({
        votesA: [...votesA, ...(winner === 'A' ? [judge_name] : [])],
        votesTie: [...votesTie, ...(winner === '-' ? [judge_name] : [])],
        votesB: [...votesB, ...(winner === 'B' ? [judge_name] : [])],
      }),
      { votesA: [], votesTie: [], votesB: [] }
    );
  }, [showVoteHistory, headToHead]);

  const iconProps = { size: 18 };
  return (
    <Stack pb={height + 32}>
      <Group justify="space-between">
        <Checkbox
          checked={showOnlyJudged}
          onChange={toggleShowOnlyJudged}
          label={
            <Text inherit c="dimmed">
              Only show head-to-heads with votes
            </Text>
          }
        />
        <Text c="dimmed" size="sm" fs="italic">
          {showOnlyJudged
            ? `${pluralize(nHeadToHeads, 'head-to-head')} with votes between selected models (${nHeadToHeadsTotal.toLocaleString()} total)`
            : `${pluralize(nHeadToHeads, 'head-to-head')} between selected models`}
        </Text>
      </Group>

      {!isLoading && nHeadToHeads === 0 ? (
        <NonIdealState
          IconComponent={IconCactus}
          description={
            <Stack align="center" gap="xs">
              <Text inherit>No head-to-heads {showOnlyJudged && 'with votes '}between selected models</Text>
              {showOnlyJudged && <Text>({pluralize(nHeadToHeadsTotal, 'total head-to-head')})</Text>}
            </Stack>
          }
        />
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

          <ControlBar ref={controlBarRef}>
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
                {showVoteHistory && (
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
                onClick={toggleShowVoteHistory}
                disabled={!hasVoteHistory}
                rightSection={<Kbd size="xs">h</Kbd>}
              >
                {!hasVoteHistory ? 'No' : showVoteHistory ? 'Hide' : 'Show'} Vote History
              </Button>
            </Box>
          </ControlBar>
        </>
      ) : (
        <></>
      )}
    </Stack>
  );
}
