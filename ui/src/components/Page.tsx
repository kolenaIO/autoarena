import { Anchor, Group, Stack, Tabs, Text, Tooltip } from '@mantine/core';
import { IconBeta, IconCrown, IconGavel, IconStack2Filled, IconSwords } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { notifications } from '@mantine/notifications';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useProject } from '../hooks/useProject.ts';
import { HeadToHead } from './HeadToHead/HeadToHead.tsx';
import { Leaderboard } from './Leaderboard/Leaderboard.tsx';
import { Judges } from './Judges/Judges.tsx';
import { ProjectSelect } from './ProjectSelect.tsx';
import { TasksDrawer } from './TasksDrawer.tsx';
import { OnboardingTimeline } from './OnboardingTimeline.tsx';

export const TAB_LEADERBOARD = 'Leaderboard';
export const TAB_COMPARISON = 'Head-to-Head';
export const TAB_JUDGES = 'Judges';
type Tab = typeof TAB_LEADERBOARD | typeof TAB_COMPARISON | typeof TAB_JUDGES;
type Props = {
  tab: Tab;
};
export function Page({ tab }: Props) {
  const { projectSlug } = useUrlState();
  const { data: project, isLoading: isLoadingProject } = useProject(projectSlug);
  const navigate = useNavigate();

  useEffect(() => {
    // TODO: this is nice functionality to have but sometimes there is a race condition where it fires after creating
    //  a project but before it loads. Disable for now
    const enableRedirect = false;
    if (enableRedirect && projectSlug != null && !isLoadingProject && project == null) {
      notifications.show({
        title: `Project '${projectSlug}' not found`,
        message: <>The project '{projectSlug}' does not seem to exist in the expected file. Redirecting home.</>,
        color: 'red',
        key: 'project-not-found',
      });
      navigate('/');
    }
  }, [project, isLoadingProject]);

  function setTab(newTab: string | null) {
    const baseUrl = `/project/${projectSlug}`;
    switch (newTab) {
      case TAB_LEADERBOARD:
        navigate(baseUrl);
        break;
      case TAB_COMPARISON:
        navigate(`${baseUrl}/compare`);
        break;
      case TAB_JUDGES:
        navigate(`${baseUrl}/judges`);
        break;
    }
  }

  const iconProps = { width: 20, height: 20, color: 'var(--mantine-color-kolena-8)' };
  return (
    <Tabs value={tab} onChange={setTab} keepMounted={false}>
      <Tabs.List bg="gray.0" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <Group align="center" p="xs" pl="lg" pr="xl" h={58}>
          <Anchor underline="never" href="/">
            <Group gap={4}>
              <IconStack2Filled color="var(--mantine-color-kolena-6)" />
              <Text fw="bold" c="black">
                AutoArena
              </Text>
              <Tooltip label="Beta Release" fz="xs">
                <IconBeta size={14} color="var(--mantine-color-ice-8)" />
              </Tooltip>
            </Group>
          </Anchor>
        </Group>
        <Tabs.Tab
          ml="xl"
          value={TAB_LEADERBOARD}
          disabled={projectSlug == null}
          leftSection={<IconCrown {...iconProps} />}
        >
          {TAB_LEADERBOARD}
        </Tabs.Tab>
        <Tabs.Tab value={TAB_COMPARISON} disabled={projectSlug == null} leftSection={<IconSwords {...iconProps} />}>
          {TAB_COMPARISON}
        </Tabs.Tab>
        <Tabs.Tab value={TAB_JUDGES} disabled={projectSlug == null} leftSection={<IconGavel {...iconProps} />}>
          {TAB_JUDGES}
        </Tabs.Tab>
        <Group gap="lg" align="center" justify="flex-end" style={{ flexGrow: 1 }} pr="lg">
          <ProjectSelect />
          <TasksDrawer />
        </Group>
      </Tabs.List>

      <Tabs.Panel value={TAB_LEADERBOARD}>
        {projectSlug != null ? (
          <Leaderboard />
        ) : (
          <Stack justify="center" align="center" h="calc(100vh - 56px)">
            <OnboardingTimeline dismissable={false} />
          </Stack>
        )}
      </Tabs.Panel>
      <Tabs.Panel value={TAB_COMPARISON}>
        <HeadToHead />
      </Tabs.Panel>
      <Tabs.Panel value={TAB_JUDGES}>
        <Judges />
      </Tabs.Panel>
    </Tabs>
  );
}
