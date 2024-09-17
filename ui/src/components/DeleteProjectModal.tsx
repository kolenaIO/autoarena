import { Code, Modal, Stack, Text } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useProject } from '../hooks/useProject.ts';
import { useDeleteProject } from '../hooks/useDeleteProject.ts';
import { ROUTES } from '../lib/routes.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function DeleteProjectModal({ isOpen, onClose }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: project } = useProject(projectSlug);
  const { mutate: deleteProject } = useDeleteProject();
  const navigate = useNavigate();

  function handleDeleteProject() {
    deleteProject(projectSlug);
    navigate(ROUTES.home());
    onClose();
  }

  return (
    <Modal opened={isOpen} centered onClose={onClose} title="Confirm Project Deletion">
      <Stack>
        <Stack gap="sm">
          <Text size="sm">
            Confirm deletion of project <Code>{project?.slug}</Code> in file:
          </Text>
          <Code block>{project?.filepath}</Code>
          <Text size="sm">Deletion will remove this file from your filesystem. This action cannot be undone.</Text>
        </Stack>
        <ConfirmOrCancelBar
          onCancel={onClose}
          onConfirm={handleDeleteProject}
          action="Delete"
          confirmButtonProps={{ color: 'red' }}
        />
      </Stack>
    </Modal>
  );
}
