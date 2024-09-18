import { ActionIcon, Code, Modal, Stack, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconTrashX } from '@tabler/icons-react';
import { useDeleteModel } from '../hooks/useDeleteModel.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { Model } from '../hooks/useModels.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

type Props = {
  model: Model;
};
export function DeleteModelButton({ model }: Props) {
  const { projectSlug = '' } = useUrlState();
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { mutate: deleteModel } = useDeleteModel({ projectSlug, modelId: model.id });

  function handleDelete() {
    deleteModel();
    close();
  }

  return (
    <>
      <ActionIcon variant="light" color="red" size="md" onClick={toggle}>
        <IconTrashX size={20} />
      </ActionIcon>
      <Modal opened={isOpen} centered onClose={close} title="Confirm Model Deletion">
        <Stack>
          <Stack gap="sm">
            <Text size="sm">Confirm deletion of model:</Text>
            <Code block>{model.name}</Code>
            <Text size="sm">This will delete the model and all associated data. This action cannot be undone.</Text>
          </Stack>
          <ConfirmOrCancelBar
            onCancel={close}
            onConfirm={handleDelete}
            action="Delete"
            confirmButtonProps={{ color: 'red' }}
          />
        </Stack>
      </Modal>
    </>
  );
}
