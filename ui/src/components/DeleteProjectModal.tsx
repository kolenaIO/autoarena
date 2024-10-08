import { Code, Modal, Stack, Text } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useUrlState, useProject, useDeleteProject, useAppRoutes } from '../hooks';
import { ConfirmOrCancelBar } from './Judges';

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function DeleteProjectModal({ isOpen, onClose }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { appRoutes } = useAppRoutes();
  const { data: project } = useProject(projectSlug);
  const { mutate: deleteProject } = useDeleteProject({ projectSlug });
  const navigate = useNavigate();

  function handleDeleteProject() {
    deleteProject();
    navigate(appRoutes.home());
    onClose();
  }

  return (
    <Modal opened={isOpen} centered onClose={onClose} title="Confirm Project Deletion">
      <Stack>
        <Stack gap="sm">
          <Text size="sm">Confirm deletion of project '{project?.slug}' at:</Text>
          <Code block>{project?.filepath}</Code>
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
