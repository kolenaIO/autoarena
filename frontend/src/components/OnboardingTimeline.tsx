import { Timeline, Text, Paper, Title, Stack, Group, Button, Anchor, Code, CloseButton, Divider } from '@mantine/core';
import { ReactNode, useEffect, useMemo, useState } from 'react';
import { IconGavel, IconPlus, IconRobot } from '@tabler/icons-react';
import { prop, sortBy } from 'ramda';
import moment, { MomentInput } from 'moment';
import { notifications } from '@mantine/notifications';
import { Judge, useJudges } from '../hooks/useJudges.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { Model, useModels } from '../hooks/useModels.ts';
import { useProjects } from '../hooks/useProjects.ts';
import { useOnboardingGuideDismissed } from '../hooks/useOnboardingGuideDismissed.ts';
import { AddModelButton } from './AddModelButton.tsx';
import { CreateProjectButton } from './CreateProjectButton.tsx';

export function OnboardingTimeline() {
  const { projectId } = useUrlState();
  const { data: projects, isLoading: isLoadingProjects } = useProjects();
  const { data: models, isLoading: isLoadingModels } = useModels(projectId);
  const { data: judges, isLoading: isLoadingJudges } = useJudges(projectId);
  const [onboardingGuideDismissed, setOnboardingGuideDismissed] = useOnboardingGuideDismissed(projectId);
  const [activeStage, setActiveStage] = useState(-1);

  const activeProject = useMemo(() => (projects ?? []).find(({ id }) => id === projectId), [projectId, projects]);
  const hasCreatedProject = activeProject != null;

  const modelsSorted = useMemo(() => sortBy<Model>(prop('created'))(models ?? []), [models]);
  const firstModel: Model | undefined = modelsSorted[0];
  const hasUploadedFirstModel = firstModel != null;
  const secondModel: Model | undefined = modelsSorted[1];
  const hasUploadedSecondModel = secondModel != null;

  const judgesSorted = useMemo(() => {
    const automatedJudges = (judges ?? []).filter(({ judge_type }) => judge_type !== 'human');
    const enabledAutomatedJudges = automatedJudges.filter(({ enabled }) => enabled);
    return sortBy<Judge>(prop('created'))(enabledAutomatedJudges);
  }, [judges]);
  const firstJudge: Judge | undefined = judgesSorted[0];
  const hasConfiguredJudge = firstJudge != null;

  const hasCompletedOnboarding = hasUploadedFirstModel && hasConfiguredJudge && hasUploadedSecondModel;

  useEffect(() => {
    setActiveStage(prevActiveStage => {
      const newActiveStage = !hasCreatedProject
        ? -1
        : !hasUploadedFirstModel
          ? 0
          : !hasConfiguredJudge
            ? 1
            : !hasUploadedSecondModel
              ? 2
              : 3;
      if (
        !onboardingGuideDismissed &&
        newActiveStage === 3 &&
        prevActiveStage < newActiveStage &&
        firstModel?.q025 == null
      ) {
        notifications.show({
          title: 'Onboarding complete',
          message:
            "Check the 'Tasks' drawer to see automated judge progress. Leaderboard will update when judging is complete",
          color: 'green',
          autoClose: 10_000,
          id: 'onboarding-complete',
        });
        setOnboardingGuideDismissed(true); // only show this message once per project
      }
      return newActiveStage;
    });
  }, [
    firstModel,
    hasCreatedProject,
    hasUploadedFirstModel,
    hasConfiguredJudge,
    hasUploadedSecondModel,
    onboardingGuideDismissed,
  ]);

  const iconProps = { size: 14 };
  const subtitleProps = { c: 'dimmed', size: 'sm', maw: 350 };
  const isLoading = isLoadingProjects || isLoadingModels || isLoadingJudges;
  return onboardingGuideDismissed || isLoading || hasCompletedOnboarding ? (
    <></>
  ) : (
    <Paper withBorder radius="md" w={600}>
      <Group bg="gray.0" p="lg" justify="space-between">
        <Title order={5}>Getting Started with AutoStack</Title>
        <CloseButton onClick={() => setOnboardingGuideDismissed(true)} />
      </Group>

      <Divider />

      <Stack p="lg" gap="lg">
        <Timeline active={activeStage} bulletSize={24} lineWidth={2}>
          <Timeline.Item
            bullet={<IconPlus {...iconProps} />}
            title={
              <TimelineItemTitle
                title="Create project"
                timestamp={activeProject?.created}
                action={activeStage === -1 ? <CreateProjectButton size="xs" /> : undefined}
              />
            }
          >
            <Text {...subtitleProps}>
              {activeProject != null
                ? `Created project '${activeProject?.name}'`
                : 'Create a project or select existing project'}
            </Text>
          </Timeline.Item>

          <Timeline.Item
            bullet={<IconRobot {...iconProps} />}
            title={
              <TimelineItemTitle
                title="Add first model"
                timestamp={firstModel?.created}
                action={activeStage === 0 ? <AddModelButton size="xs" /> : undefined}
              />
            }
          >
            <Text {...subtitleProps}>
              {firstModel != null ? (
                `Added model '${firstModel?.name}'`
              ) : (
                <Text>
                  Add a model by uploading a CSV with <Code>prompt</Code> and <Code>response</Code> columns
                </Text>
              )}
            </Text>
          </Timeline.Item>

          <Timeline.Item
            bullet={<IconGavel {...iconProps} />}
            title={
              <TimelineItemTitle
                title="Configure automated judge"
                timestamp={firstJudge?.created}
                action={
                  activeStage === 1 ? (
                    <Anchor href={`/project/${projectId}/judges`}>
                      <Button leftSection={<IconGavel size={18} />} size="xs">
                        Configure Judge
                      </Button>
                    </Anchor>
                  ) : undefined
                }
              />
            }
          >
            <Text {...subtitleProps}>
              {firstJudge != null
                ? `Configured judge '${firstJudge.name}'`
                : "Visit the 'Judges' tab to configure an automated judge"}
            </Text>
          </Timeline.Item>

          <Timeline.Item
            bullet={<IconRobot {...iconProps} />}
            title={
              <TimelineItemTitle
                title="Add second model"
                timestamp={secondModel?.created}
                action={activeStage === 2 ? <AddModelButton size="xs" /> : undefined}
              />
            }
          >
            <Text {...subtitleProps}>
              Add a second model to compare{firstModel != null && ` against '${firstModel.name}'`}
              {firstJudge != null && ` using '${firstJudge.name}' as judge`}
            </Text>
          </Timeline.Item>
        </Timeline>
      </Stack>
    </Paper>
  );
}

type TimelineItemTitleProps = {
  title: string;
  timestamp?: MomentInput;
  action?: ReactNode;
};
function TimelineItemTitle({ title, timestamp, action }: TimelineItemTitleProps) {
  return (
    <Group justify="space-between" align="flex-start">
      <Text>{title}</Text>
      {timestamp != null && (
        <Text c="dimmed" size="xs">
          {moment(timestamp).fromNow()}
        </Text>
      )}
      {action}
    </Group>
  );
}
