import { Code, Modal, Stack, Text } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useUrlState, useProject, useDeleteProject } from '../hooks';
import { ROUTES } from '../lib';
import { ConfirmOrCancelBar } from './Judges';

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function DeleteProjectModal({ isOpen, onClose }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: project } = useProject(projectSlug);
  const { mutate: deleteProject } = useDeleteProject({ projectSlug });
  const navigate = useNavigate();

  function handleDeleteProject() {
    deleteProject();
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
