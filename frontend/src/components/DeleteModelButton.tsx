import { Button, Code, Modal, Stack, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';
import { RankedModel } from './Leaderboard/types.ts';

type Props = {
  model: RankedModel;
};
export function DeleteModelButton({ model }: Props) {
  const [isOpen, { toggle, close }] = useDisclosure(false);

  function handleDelete() {
    console.log('delete');
  }

  return (
    <>
      <Button variant="light" color="red" onClick={toggle}>
        Delete
      </Button>
      <Modal
        opened={isOpen}
        centered
        onClose={close}
        title="Confirm Model Deletion"
        transitionProps={{ transition: 'fade', duration: 100 }}
      >
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
            buttonProps={{ color: 'red' }}
          />
        </Stack>
      </Modal>
    </>
  );
}
