import { Group, Stack, Tabs } from '@mantine/core';
import { IconCrown, IconGavel, IconSwords } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { notifications } from '@mantine/notifications';
import { useProject, useAppRoutes, useUrlState } from '../hooks';
import { HeadToHead } from './HeadToHead';
import { Leaderboard } from './Leaderboard';
import { Judges } from './Judges';
import { ProjectSelect } from './ProjectSelect.tsx';
import { TasksDrawer } from './TasksDrawer';
import { OnboardingTimeline } from './OnboardingTimeline.tsx';
import { MainMenu } from './MainMenu.tsx';
import { Tab } from './types.ts';

type Props = {
  tab: Tab;
};
export function Page({ tab }: Props) {
  const { projectSlug } = useUrlState();
  const { appRoutes } = useAppRoutes();
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
      navigate(appRoutes.home());
    }
  }, [project, isLoadingProject]);

  function setTab(newTab: string | null) {
    switch (newTab) {
      case Tab.LEADERBOARD:
        navigate(appRoutes.leaderboard(projectSlug ?? ''));
        break;
      case Tab.COMPARISON:
        navigate(appRoutes.compare(projectSlug ?? ''));
        break;
      case Tab.JUDGES:
        navigate(appRoutes.judges(projectSlug ?? ''));
        break;
    }
  }

  const iconProps = { size: 20, color: 'var(--mantine-color-kolena-light-color)' };
  return (
    <Tabs value={tab} onChange={setTab} keepMounted={false}>
      <Tabs.List bg="gray.0" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <Group align="center" p="xs" pl="lg" pr="xl" h={58}>
          <MainMenu />
        </Group>
        <Tabs.Tab
          ml="xl"
          value={Tab.LEADERBOARD}
          disabled={projectSlug == null}
          leftSection={<IconCrown {...iconProps} />}
        >
          {Tab.LEADERBOARD}
        </Tabs.Tab>
        <Tabs.Tab value={Tab.COMPARISON} disabled={projectSlug == null} leftSection={<IconSwords {...iconProps} />}>
          {Tab.COMPARISON}
        </Tabs.Tab>
        <Tabs.Tab value={Tab.JUDGES} disabled={projectSlug == null} leftSection={<IconGavel {...iconProps} />}>
          {Tab.JUDGES}
        </Tabs.Tab>
        <Group gap="lg" align="center" justify="flex-end" style={{ flexGrow: 1 }} pr="lg">
          <ProjectSelect />
          <TasksDrawer />
        </Group>
      </Tabs.List>

      <Tabs.Panel value={Tab.LEADERBOARD}>
        {projectSlug != null ? (
          <Leaderboard />
        ) : (
          <Stack justify="center" align="center" h="calc(100vh - 58px)">
            <OnboardingTimeline dismissable={false} />
          </Stack>
        )}
      </Tabs.Panel>
      <Tabs.Panel value={Tab.COMPARISON}>
        <HeadToHead />
      </Tabs.Panel>
      <Tabs.Panel value={Tab.JUDGES}>
        <Judges />
      </Tabs.Panel>
    </Tabs>
  );
}
