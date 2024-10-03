import { Timeline, Text, Paper, Title, Stack, Group, Button, Code, CloseButton, Divider, Anchor } from '@mantine/core';
import { ReactNode, useEffect, useMemo, useState } from 'react';
import { IconGavel, IconPlus, IconRobot } from '@tabler/icons-react';
import { prop, sortBy } from 'ramda';
import moment, { MomentInput } from 'moment';
import { Link, useNavigate } from 'react-router-dom';
import {
  Judge,
  useJudges,
  useUrlState,
  Model,
  useModels,
  useOnboardingGuideDismissed,
  useProjects,
  useProject,
  useAppRoutes,
} from '../hooks';
import { AddModelButton } from './AddModelButton.tsx';
import { CreateProjectButton } from './CreateProjectButton.tsx';
import { ProjectSelect } from './ProjectSelect.tsx';

type Props = {
  dismissable?: boolean;
};
export function OnboardingTimeline({ dismissable = true }: Props) {
  const { projectSlug } = useUrlState();
  const { appRoutes } = useAppRoutes();
  const navigate = useNavigate();
  const { data: projects } = useProjects();
  const { data: activeProject, isLoading: isLoadingProjects } = useProject(projectSlug);
  const { data: models, isLoading: isLoadingModels } = useModels(projectSlug);
  const { data: judges, isLoading: isLoadingJudges } = useJudges(projectSlug);
  const [onboardingGuideDismissed, setOnboardingGuideDismissed] = useOnboardingGuideDismissed(projectSlug);
  const [activeStage, setActiveStage] = useState(-1);

  const hasCreatedProject = activeProject != null;

  const modelsSorted = useMemo(() => sortBy<Model>(prop('created'))(models ?? []), [models]);
  const hasUploadedTwoModels = modelsSorted.length >= 2;

  const judgesSorted = useMemo(() => {
    const automatedJudges = (judges ?? []).filter(({ judge_type }) => judge_type !== 'human');
    const enabledAutomatedJudges = automatedJudges.filter(({ enabled }) => enabled);
    return sortBy<Judge>(prop('created'))(enabledAutomatedJudges);
  }, [judges]);
  const firstJudge: Judge | undefined = judgesSorted[0];
  const hasConfiguredJudge = firstJudge != null;

  const hasCompletedOnboarding = hasConfiguredJudge && hasUploadedTwoModels;

  useEffect(() => {
    setActiveStage(prevActiveStage => {
      const newActiveStage = !hasCreatedProject ? -1 : !hasConfiguredJudge ? 0 : !hasUploadedTwoModels ? 1 : 2;
      if (!onboardingGuideDismissed && newActiveStage === 3 && prevActiveStage < newActiveStage) {
        setOnboardingGuideDismissed(true); // only show this message once per project
      }
      return newActiveStage;
    });
  }, [hasCreatedProject, hasConfiguredJudge, hasUploadedTwoModels, onboardingGuideDismissed]);

  const hasProjects = projects?.length ?? 0 > 0;
  const iconProps = { size: 14 };
  const subtitleProps = { c: 'dimmed', size: 'sm', maw: 350 };
  const isLoading = isLoadingProjects || isLoadingModels || isLoadingJudges;
  const isDismissed = dismissable && onboardingGuideDismissed;
  return isDismissed || isLoading || hasCompletedOnboarding ? (
    <></>
  ) : (
    <Paper withBorder radius="md" w={600} shadow="sm" style={{ overflow: 'hidden' }}>
      <Group bg="gray.0" p="lg" justify="space-between">
        <Title order={5}>Getting Started with AutoArena</Title>
        {dismissable && <CloseButton onClick={() => setOnboardingGuideDismissed(true)} />}
      </Group>

      <Divider />

      <Stack p="lg" gap="lg">
        <Timeline active={activeStage} bulletSize={24} lineWidth={2}>
          <Timeline.Item
            bullet={<IconPlus {...iconProps} />}
            title={
              <TimelineItemTitle
                title={hasProjects ? 'Select a project' : 'Create your first project'}
                action={
                  activeStage !== -1 ? undefined : hasProjects ? <ProjectSelect /> : <CreateProjectButton size="xs" />
                }
              />
            }
          >
            <Text {...subtitleProps}>
              {activeProject != null ? (
                <>
                  Created project '{activeProject?.slug}' at <Code>{activeProject?.filepath}</Code>
                </>
              ) : hasProjects ? (
                'Select a project or create a new one'
              ) : (
                'Create a new project file'
              )}
            </Text>
          </Timeline.Item>

          <Timeline.Item
            bullet={<IconGavel {...iconProps} />}
            title={
              <TimelineItemTitle
                title="Configure an automated judge"
                timestamp={firstJudge?.created}
                action={
                  activeStage === 0 ? (
                    <Link to={appRoutes.judges(projectSlug ?? '')}>
                      <Button leftSection={<IconGavel size={18} />} size="xs">
                        Configure Judge
                      </Button>
                    </Link>
                  ) : undefined
                }
              />
            }
          >
            <Text {...subtitleProps}>
              {firstJudge != null ? (
                `Configured judge '${firstJudge.name}'`
              ) : (
                <>
                  Visit the{' '}
                  {projectSlug != null ? (
                    <Anchor onClick={() => navigate(appRoutes.judges(projectSlug))}>Judges</Anchor>
                  ) : (
                    'Judges'
                  )}{' '}
                  tab to configure an automated judge
                </>
              )}
            </Text>
          </Timeline.Item>

          <Timeline.Item
            bullet={<IconRobot {...iconProps} />}
            title={
              <TimelineItemTitle
                title="Add responses from two models"
                timestamp={modelsSorted[1]?.created}
                action={activeStage === 1 ? <AddModelButton size="xs" /> : undefined}
              />
            }
          >
            <Text {...subtitleProps}>
              {modelsSorted[0] != null ? (
                `Added first model '${modelsSorted[0]?.name}' ${moment(modelsSorted[0]?.created).fromNow()}`
              ) : (
                <Text>
                  Add two models to evaluate by uploading CSVs with <Code>prompt</Code> and <Code>response</Code>{' '}
                  columns
                </Text>
              )}
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
