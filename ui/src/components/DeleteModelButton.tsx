import { Button, Code, Modal, Stack, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconX } from '@tabler/icons-react';
import { useDeleteModel } from '../hooks/useDeleteModel.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { Model } from '../hooks/useModels.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

type Props = {
  model: Model;
};
export function DeleteModelButton({ model }: Props) {
  const { projectId = -1 } = useUrlState();
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { mutate: deleteModel } = useDeleteModel({ projectId });

  function handleDelete() {
    deleteModel(model.id);
    close();
  }

  return (
    <>
      <Button variant="light" color="red" onClick={toggle} leftSection={<IconX />}>
        Delete
      </Button>
      <Modal opened={isOpen} centered onClose={close} title="Confirm Model Deletion">
        <Stack>
          <Stack gap="sm">
            <Text size="sm">Confirm deletion of model:</Text>
            <Code block>{model.name}</Code>
            <Text size="sm">This action cannot be undone.</Text>
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
