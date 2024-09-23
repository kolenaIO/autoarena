import { ActionIcon, Loader, Menu } from '@mantine/core';
import { IconAdjustmentsHorizontal, IconCalculator, IconTrashX } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useRecomputeLeaderboard, useUrlState } from '../../hooks';
import { DeleteProjectModal } from '../DeleteProjectModal.tsx';

export function LeaderboardSettings() {
  const { projectSlug = '' } = useUrlState();
  const { mutate: recomputeLeaderboard, isPending } = useRecomputeLeaderboard({ projectSlug });
  const [isDeleteProjectModalOpen, { toggle, close }] = useDisclosure(false);

  return (
    <Menu shadow="md" position="bottom-end">
      <Menu.Target>
        <ActionIcon variant="subtle" color="gray" size="lg">
          <IconAdjustmentsHorizontal />
        </ActionIcon>
      </Menu.Target>

      <Menu.Dropdown>
        <Menu.Item
          leftSection={isPending ? <Loader size={18} /> : <IconCalculator />}
          onClick={() => recomputeLeaderboard()}
        >
          Recompute Leaderboard
        </Menu.Item>
        <Menu.Item leftSection={<IconTrashX />} onClick={toggle}>
          Delete Project
        </Menu.Item>
      </Menu.Dropdown>

      <DeleteProjectModal isOpen={isDeleteProjectModalOpen} onClose={close} />
    </Menu>
  );
}
