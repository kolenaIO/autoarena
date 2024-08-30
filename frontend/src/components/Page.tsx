import { Button, Flex, Group, Stack, Tabs, Text } from '@mantine/core';
import { IconClick, IconColumns2, IconCpu, IconCrown, IconGavel } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { HeadToHead } from './HeadToHead.tsx';
import { Leaderboard } from './Leaderboard.tsx';
import { KolenaLogo } from './KolenaLogo.tsx';
import { Judges } from './Judges.tsx';
import { ProjectSelect } from './ProjectSelect.tsx';
import { useUrlState } from './useUrlState.ts';
import { NonIdealState } from './NonIdealState.tsx';

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
  const navigate = useNavigate();

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
  const selectProject = (
    <Stack justify="center" h="calc(100vh - 56px)">
      <NonIdealState IconComponent={IconClick} description="Select a project to get started" />
    </Stack>
  );
  return (
    <Tabs value={tab} onChange={setTab} keepMounted={false}>
      <Tabs.List bg="gray.0" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <Group align="center" p="xs" pl="lg">
          <Group align="center" c="kolena.8" style={{ height: 24, width: 24 }}>
            <KolenaLogo />
          </Group>
          <Text fw="bold">AutoStack</Text>
          <ProjectSelect />
        </Group>
        <div style={{ width: 96 }} />
        <Tabs.Tab value={TAB_LEADERBOARD} disabled={projectId == null} leftSection={<IconCrown {...iconProps} />}>
          {TAB_LEADERBOARD}
        </Tabs.Tab>
        <Tabs.Tab value={TAB_COMPARISON} disabled={projectId == null} leftSection={<IconColumns2 {...iconProps} />}>
          {TAB_COMPARISON}
        </Tabs.Tab>
        {/* <Tabs.Tab value={TAB_STATISTICS} leftSection={<IconDeviceDesktopAnalytics {...iconProps} />}>
          {TAB_STATISTICS}
        </Tabs.Tab> */}
        <Tabs.Tab value={TAB_JUDGES} disabled={projectId == null} leftSection={<IconGavel {...iconProps} />}>
          {TAB_JUDGES}
        </Tabs.Tab>
        <Flex align="center" justify="flex-end" style={{ flexGrow: 1 }} pr="lg">
          <Button variant="light" leftSection={<IconCpu {...iconProps} />}>
            Jobs
          </Button>
        </Flex>
      </Tabs.List>

      <Tabs.Panel value={TAB_LEADERBOARD}>{projectId != null ? <Leaderboard /> : selectProject}</Tabs.Panel>
      <Tabs.Panel value={TAB_COMPARISON}>{projectId != null ? <HeadToHead /> : selectProject}</Tabs.Panel>
      {/* <Tabs.Panel value={TAB_STATISTICS}>Stats</Tabs.Panel> */}
      <Tabs.Panel value={TAB_JUDGES}>{projectId != null ? <Judges /> : selectProject}</Tabs.Panel>
    </Tabs>
  );
}
