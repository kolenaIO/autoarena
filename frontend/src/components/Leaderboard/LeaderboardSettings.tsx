import { ActionIcon, Loader, Menu } from '@mantine/core';
import { IconAdjustmentsHorizontal, IconCalculator } from '@tabler/icons-react';
import { useRecomputeLeaderboard } from '../../hooks/useRecomputeLeaderboard.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';

export function LeaderboardSettings() {
  const { projectId = -1 } = useUrlState();
  const { mutate: recomputeLeaderboard, isPending } = useRecomputeLeaderboard({ projectId });

  return (
    <Menu shadow="md" position="bottom-end">
      <Menu.Target>
        <ActionIcon variant="subtle" color="gray" size="lg">
          <IconAdjustmentsHorizontal />
        </ActionIcon>
      </Menu.Target>

      <Menu.Dropdown>
        <Menu.Item leftSection={isPending ? <Loader size={18} /> : <IconCalculator />} onClick={recomputeLeaderboard}>
          Recompute Leaderboard
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  );
}
