import { Box, Button, Group, Kbd, Paper, SimpleGrid, Stack, Text } from '@mantine/core';
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
import { ExtraResultData } from './ExtraResultData.tsx';

type Props = {
  modelAId: number;
  modelBId: number;
};
export function HeadToHeadTwoModels({ modelAId, modelBId }: Props) {
  const { projectId = -1 } = useUrlState();
  const navigate = useNavigate();
  const [showJudgingHistory, { toggle: toggleShowJudgingHistory }] = useDisclosure(false);
  const { data: headToHeads, isLoading } = useHeadToHeads({ modelAId, modelBId });
  const { mutate: submitJudgement } = useSubmitHeadToHeadJudgement({ projectId });
  const [h2hIndex, setH2hIndex] = useState(0);
  const h2h = useMemo(() => headToHeads?.[h2hIndex], [headToHeads, h2hIndex]);
  const nHeadToHeads: number = headToHeads?.length ?? 0;

  useEffect(() => {
    setH2hIndex(0);
  }, [modelAId, modelBId]);

  function navigatePrevious() {
    setH2hIndex(prev => Math.max(0, prev - 1));
  }
  function navigateNext() {
    setH2hIndex(prev => Math.min(prev + 1, nHeadToHeads - 1));
  }

  function submitVote(vote: 'A' | 'B' | '-') {
    return () => {
      if (h2h != null) {
        submitJudgement({
          project_id: projectId,
          result_a_id: h2h.result_a.id,
          result_b_id: h2h.result_b.id,
          winner: vote,
        });
        setH2hIndex(prev => prev + 1);
      }
    };
  }

  useHotkeys([
    ['ArrowLeft', submitVote('A')],
    ['ArrowDown', submitVote('-')],
    ['ArrowRight', submitVote('B')],
    ['p', navigatePrevious],
    ['n', navigateNext],
    ['j', toggleShowJudgingHistory],
  ]);

  const hasJudgingHistory = (h2h?.history?.length ?? 0) > 0;
  const { votesA, votesTie, votesB } = useMemo(() => {
    return (h2h?.history ?? []).reduce<{ votesA: string[]; votesTie: string[]; votesB: string[] }>(
      ({ votesA, votesTie, votesB }, { winner, judge_name }) => ({
        votesA: [...votesA, ...(winner === 'A' ? [judge_name] : [])],
        votesTie: [...votesTie, ...(winner === '-' ? [judge_name] : [])],
        votesB: [...votesB, ...(winner === 'B' ? [judge_name] : [])],
      }),
      { votesA: [], votesTie: [], votesB: [] }
    );
  }, [showJudgingHistory, h2h]);

  const iconProps = { size: 18 };
  return !isLoading && nHeadToHeads === 0 ? (
    <NonIdealState IconComponent={IconCactus} description="No head-to-head matchups between selected models" />
  ) : !isLoading && h2hIndex > nHeadToHeads - 1 ? (
    <NonIdealState
      IconComponent={IconBalloon}
      description={
        <Stack>
          <Text>Judged all {nHeadToHeads.toLocaleString()} head-to-head matchups between selected models</Text>
          <Button onClick={() => navigate(`/project/${projectId}`)}>View Leaderboard</Button>
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
          <MarkdownContent>{`**Prompt:** ${h2h?.result_a?.prompt}`}</MarkdownContent>
        </Paper>
        <SimpleGrid cols={2}>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response A:**\n\n${h2h?.result_a.response}`}</MarkdownContent>
          </Paper>
          <Paper withBorder p="md" flex={1} style={{ overflow: 'auto' }}>
            <MarkdownContent>{`**Response B:**\n\n${h2h?.result_b.response}`}</MarkdownContent>
          </Paper>
          <ExtraResultData extra={h2h?.result_a?.extra} />
          <ExtraResultData extra={h2h?.result_b?.extra} />
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
              disabled={h2hIndex < 1}
            >
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
            <Button
              rightSection={<Kbd>n</Kbd>}
              variant="subtle"
              color="gray"
              onClick={navigateNext}
              disabled={h2hIndex >= nHeadToHeads - 1}
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
