import { Flex, Group, Stack, Tabs, Text } from '@mantine/core';
import { IconCrown, IconGavel, IconStack2Filled, IconSwords } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useProjects } from '../hooks/useProjects.ts';
import { HeadToHead } from './HeadToHead/HeadToHead.tsx';
import { Leaderboard } from './Leaderboard/Leaderboard.tsx';
import { Judges } from './Judges/Judges.tsx';
import { ProjectSelect } from './ProjectSelect.tsx';
import { TasksDrawer } from './TasksDrawer.tsx';
import { OnboardingTimeline } from './OnboardingTimeline.tsx';

export const TAB_LEADERBOARD = 'Leaderboard';
export const TAB_COMPARISON = 'Head-to-Head';
export const TAB_STATISTICS = 'Statistics';
export const TAB_JUDGES = 'Judges';
type Tab = typeof TAB_LEADERBOARD | typeof TAB_COMPARISON | typeof TAB_STATISTICS | typeof TAB_JUDGES;
type Props = {
  tab: Tab;
};
export function Page({ tab }: Props) {
  const { projectId } = useUrlState();
  const { data: projects } = useProjects();
  const navigate = useNavigate();

  useEffect(() => {
    // redirect home if we have a stale URL referencing a project that doesn't exist
    if (projects != null && projects.length === 0) {
      navigate('/');
    }
  }, [projects]);

  function setTab(newTab: string | null) {
    const baseUrl = `/project/${projectId}`;
    switch (newTab) {
      case TAB_LEADERBOARD:
        navigate(baseUrl);
        break;
      case TAB_COMPARISON:
        navigate(`${baseUrl}/compare`);
        break;
      case TAB_STATISTICS:
        navigate(`${baseUrl}/statistics`);
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
        <Group align="center" p="xs" pl="lg">
          <Group gap={4}>
            <IconStack2Filled color="var(--mantine-color-kolena-8)" />
            <Text fw="bold">AutoStack</Text>
          </Group>
          <ProjectSelect />
        </Group>
        <div style={{ width: 96 }} />
        <Tabs.Tab value={TAB_LEADERBOARD} disabled={projectId == null} leftSection={<IconCrown {...iconProps} />}>
          {TAB_LEADERBOARD}
        </Tabs.Tab>
        <Tabs.Tab value={TAB_COMPARISON} disabled={projectId == null} leftSection={<IconSwords {...iconProps} />}>
          {TAB_COMPARISON}
        </Tabs.Tab>
        {/* <Tabs.Tab value={TAB_STATISTICS} leftSection={<IconDeviceDesktopAnalytics {...iconProps} />}>
          {TAB_STATISTICS}
        </Tabs.Tab> */}
        <Tabs.Tab value={TAB_JUDGES} disabled={projectId == null} leftSection={<IconGavel {...iconProps} />}>
          {TAB_JUDGES}
        </Tabs.Tab>
        <Flex align="center" justify="flex-end" style={{ flexGrow: 1 }} pr="lg">
          <TasksDrawer />
        </Flex>
      </Tabs.List>

      <Tabs.Panel value={TAB_LEADERBOARD}>
        {projectId != null ? (
          <Leaderboard />
        ) : (
          <Stack justify="center" align="center" h="calc(100vh - 56px)">
            <OnboardingTimeline />
          </Stack>
        )}
      </Tabs.Panel>
      <Tabs.Panel value={TAB_COMPARISON}>
        <HeadToHead />
      </Tabs.Panel>
      {/* <Tabs.Panel value={TAB_STATISTICS}>Stats</Tabs.Panel> */}
      <Tabs.Panel value={TAB_JUDGES}>
        <Judges />
      </Tabs.Panel>
    </Tabs>
  );
}
