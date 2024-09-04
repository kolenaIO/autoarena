import { Code, Modal, Stack, Text } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useProject } from '../hooks/useProject.ts';
import { useDeleteProject } from '../hooks/useDeleteProject.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function DeleteProjectModal({ isOpen, onClose }: Props) {
  const { projectId = -1 } = useUrlState();
  const { data: project } = useProject(projectId);
  const { mutate: deleteProject } = useDeleteProject();
  const navigate = useNavigate();

  function handleDeleteProject() {
    deleteProject(projectId);
    navigate('/');
    onClose();
  }

  return (
    <Modal opened={isOpen} centered onClose={onClose} title="Confirm Project Deletion">
      <Stack>
        <Stack gap="sm">
          <Text size="sm">Confirm deletion of project:</Text>
          <Code block>{project?.name}</Code>
          <Text size="sm">This action cannot be undone.</Text>
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
