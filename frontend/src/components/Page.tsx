import { Button, Flex, Group, Select, Tabs, Text } from '@mantine/core';
import { IconColumns2, IconCpu, IconCrown, IconGavel } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { HeadToHead } from './HeadToHead.tsx';
import { Leaderboard } from './Leaderboard.tsx';
import { KolenaLogo } from './KolenaLogo.tsx';
import { Judges } from './Judges.tsx';

export const DUMMY_DEFAULT_PROJECT = 'LMsys Rankings';

export const TAB_LEADERBOARD = 'Leaderboard';
export const TAB_COMPARISON = 'Head-to-Head';
export const TAB_STATISTICS = 'Statistics';
export const TAB_JUDGES = 'Judges';
type Tab = typeof TAB_LEADERBOARD | typeof TAB_COMPARISON | typeof TAB_STATISTICS | typeof TAB_JUDGES;
type Props = {
  tab: Tab;
};
export function Page({ tab }: Props) {
  const navigate = useNavigate();

  function setTab(newTab: string | null) {
    switch (newTab) {
      case TAB_LEADERBOARD:
        navigate('/');
        break;
      case TAB_COMPARISON:
        navigate('/compare');
        break;
      case TAB_STATISTICS:
        navigate('/statistics');
        break;
      case TAB_JUDGES:
        navigate('/judges');
        break;
    }
  }

  const iconProps = { width: 20, height: 20, color: 'var(--mantine-color-kolena-8)' };
  return (
    <Tabs value={tab} onChange={setTab} keepMounted={false}>
      <Tabs.List bg="gray.0" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <Group align="center" p="xs" pl="lg">
          <Group align="center" c="kolena.8" style={{ height: 24, width: 24 }}>
            <KolenaLogo />
          </Group>
          <Text fw="bold">AutoStack</Text>
          <Select
            variant="filled"
            placeholder="Select Project"
            data={[DUMMY_DEFAULT_PROJECT]}
            defaultValue={DUMMY_DEFAULT_PROJECT}
            allowDeselect={false}
          />
        </Group>
        <div style={{ width: 96 }} />
        <Tabs.Tab value={TAB_LEADERBOARD} leftSection={<IconCrown {...iconProps} />}>
          {TAB_LEADERBOARD}
        </Tabs.Tab>
        <Tabs.Tab value={TAB_COMPARISON} leftSection={<IconColumns2 {...iconProps} />}>
          {TAB_COMPARISON}
        </Tabs.Tab>
        {/* <Tabs.Tab value={TAB_STATISTICS} leftSection={<IconDeviceDesktopAnalytics {...iconProps} />}>
          {TAB_STATISTICS}
        </Tabs.Tab> */}
        <Tabs.Tab value={TAB_JUDGES} leftSection={<IconGavel {...iconProps} />}>
          {TAB_JUDGES}
        </Tabs.Tab>
        <Flex align="center" justify="flex-end" style={{ flexGrow: 1 }} pr="lg">
          <Button variant="light" leftSection={<IconCpu {...iconProps} />}>
            Jobs
          </Button>
        </Flex>
      </Tabs.List>

      <Tabs.Panel value={TAB_LEADERBOARD}>
        <Leaderboard />
      </Tabs.Panel>
      <Tabs.Panel value={TAB_COMPARISON}>
        <HeadToHead />
      </Tabs.Panel>
      <Tabs.Panel value={TAB_STATISTICS}>Stats</Tabs.Panel>
      <Tabs.Panel value={TAB_JUDGES}>
        <Judges />
      </Tabs.Panel>
    </Tabs>
  );
}
