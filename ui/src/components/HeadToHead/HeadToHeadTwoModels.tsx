import { Box, Button, Group, Kbd, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core';
import {
  IconArrowDown,
  IconArrowLeft,
  IconArrowRight,
  IconArrowUp,
  IconBalloon,
  IconCactus,
} from '@tabler/icons-react';
import { Fragment, useEffect, useMemo, useState } from 'react';
import { useDisclosure, useElementSize, useHotkeys } from '@mantine/hooks';
import { useNavigate } from 'react-router-dom';
import { useHeadToHeads, useUrlState, useSubmitHeadToHeadVote, useModel, useAppRoutes } from '../../hooks';
import { pluralize } from '../../lib';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { NonIdealState } from '../NonIdealState.tsx';
import { ControlBar } from './ControlBar.tsx';

type ShowMode = 'All' | 'With Votes' | 'Without Votes';

type Props = {
  modelAId: number;
  modelBId: number;
};
export function HeadToHeadTwoModels({ modelAId, modelBId }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { appRoutes } = useAppRoutes();
  const navigate = useNavigate();
  const [showVoteHistory, { toggle: toggleShowVoteHistory }] = useDisclosure(false);
  const { data: allHeadToHeads, isLoading } = useHeadToHeads({ projectSlug, modelAId, modelBId });
  const { data: modelA } = useModel(projectSlug, modelAId);
  const { data: modelB } = useModel(projectSlug, modelBId);
  const { mutate: submitJudgement, isPending } = useSubmitHeadToHeadVote({ projectSlug });
  const [headToHeadIndex, setHeadToHeadIndex] = useState(0);
  const { ref: controlBarRef, height } = useElementSize<HTMLDivElement>();
  const [showMode, setShowMode] = useState<ShowMode>('All');

  const headToHeads = useMemo(() => {
    switch (showMode) {
      case 'All':
        return allHeadToHeads ?? [];
      case 'With Votes':
        return (allHeadToHeads ?? []).filter(({ history }) => history.length > 0);
      case 'Without Votes':
        return (allHeadToHeads ?? []).filter(({ history }) => history.length === 0);
    }
  }, [allHeadToHeads, showMode]);
  const headToHead = useMemo(() => headToHeads[headToHeadIndex], [headToHeads, headToHeadIndex]);
  const nHeadToHeadsTotal = (allHeadToHeads ?? []).length;
  const nHeadToHeads = headToHeads.length;

  useEffect(() => {
    setHeadToHeadIndex(0);
  }, [modelAId, modelBId]);

  function navigateBack() {
    setHeadToHeadIndex(prev => Math.max(0, prev - 1));
  }
  function navigateNext() {
    setHeadToHeadIndex(prev => Math.min(prev + 1, nHeadToHeads - 1));
  }

  function submitVote(vote: 'A' | 'B' | '-') {
    return () => {
      if (headToHead != null && !isPending) {
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
    ['b', navigateBack],
    ['n', navigateNext],
    ['h', toggleShowVoteHistory],
  ]);

  const hasVoteHistory = (headToHead?.history?.length ?? 0) > 0;
  const modelNames = modelA != null && modelB != null ? `'${modelA.name}' and '${modelB.name}'` : 'selected models';
  const iconProps = { size: 18 };
  return (
    <Stack pb={Math.max(height, 100) + 32}>
      <Group justify="space-between">
        <Paper withBorder>
          <Button.Group>
            <Button
              size="xs"
              color="gray"
              variant={showMode === 'All' ? 'light' : 'subtle'}
              onClick={() => setShowMode('All')}
            >
              Show All
            </Button>
            <Button
              size="xs"
              color="gray"
              variant={showMode === 'With Votes' ? 'light' : 'subtle'}
              onClick={() => setShowMode('With Votes')}
            >
              Show With Votes
            </Button>
            <Button
              size="xs"
              color="gray"
              variant={showMode === 'Without Votes' ? 'light' : 'subtle'}
              onClick={() => setShowMode('Without Votes')}
            >
              Show Without Votes
            </Button>
          </Button.Group>
        </Paper>
        <Text c="dimmed" size="sm" fs="italic">
          {showMode === 'All'
            ? `${pluralize(nHeadToHeads, 'head-to-head')} between ${modelNames}`
            : `${pluralize(nHeadToHeads, 'head-to-head')} ${showMode.toLowerCase()} between ${modelNames} (${nHeadToHeadsTotal.toLocaleString()} total)`}
        </Text>
      </Group>

      {!isLoading && nHeadToHeads === 0 ? (
        <Paper withBorder bg="white" p="xl">
          <NonIdealState
            IconComponent={IconCactus}
            description={
              <Stack align="center" gap="xs">
                <Text inherit>
                  No head-to-heads {showMode !== 'All' && `${showMode.toLowerCase()} `}between {modelNames}
                </Text>
                {showMode !== 'All' && <Text>({pluralize(nHeadToHeadsTotal, 'total head-to-head')})</Text>}
              </Stack>
            }
          />
        </Paper>
      ) : !isLoading && headToHeadIndex > nHeadToHeads - 1 ? (
        <Paper withBorder bg="white" p="xl">
          <NonIdealState
            IconComponent={IconBalloon}
            description={
              <Stack>
                <Text>
                  Judged all {nHeadToHeads.toLocaleString()} head-to-head matchups between {modelNames}
                </Text>
                <Button onClick={() => navigate(appRoutes.leaderboard(projectSlug))}>View Leaderboard</Button>
              </Stack>
            }
          />
        </Paper>
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
              <Title order={5}>Which response is better?</Title>
              <SimpleGrid cols={5} spacing="xs">
                <Button
                  leftSection={<Kbd>b</Kbd>}
                  variant="subtle"
                  color="gray"
                  onClick={navigateBack}
                  disabled={headToHeadIndex < 1}
                  h="100%"
                >
                  Back
                </Button>
                <Button
                  leftSection={<IconArrowLeft {...iconProps} />}
                  variant="light"
                  onClick={submitVote('A')}
                  h="100%"
                  disabled={isPending}
                >
                  Left is Better
                </Button>
                <Stack gap={4}>
                  <Button
                    size="compact-xs"
                    variant="light"
                    leftSection={<IconArrowUp {...iconProps} />}
                    onClick={submitVote('-')}
                    disabled={isPending}
                  >
                    Both are Good
                  </Button>
                  <Button
                    size="compact-xs"
                    variant="light"
                    leftSection={<IconArrowDown {...iconProps} />}
                    onClick={submitVote('-')}
                    disabled={isPending}
                  >
                    Both are Bad
                  </Button>
                </Stack>
                <Button
                  rightSection={<IconArrowRight {...iconProps} />}
                  variant="light"
                  onClick={submitVote('B')}
                  h="100%"
                  disabled={isPending}
                >
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
                {showVoteHistory &&
                  headToHead?.history?.map(({ winner, judge_name }, i) => (
                    <Fragment key={`${headToHeadIndex}-${i}`}>
                      <div />
                      <Text maw={150} ta="center" fz="xs" truncate="end">
                        {winner === 'A' ? judge_name : undefined}
                      </Text>
                      <Text maw={150} ta="center" fz="xs" truncate="end">
                        {winner !== 'A' && winner !== 'B' ? judge_name : undefined}
                      </Text>
                      <Text maw={150} ta="center" fz="xs" truncate="end">
                        {winner === 'B' ? judge_name : undefined}
                      </Text>
                      <div />
                    </Fragment>
                  ))}
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
