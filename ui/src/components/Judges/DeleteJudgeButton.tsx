import { Button, Code, Modal, Stack, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useDeleteJudge } from '../../hooks/useDeleteJudge.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { Judge } from '../../hooks/useJudges.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';

type Props = {
  judge: Judge;
};
export function DeleteJudgeButton({ judge }: Props) {
  const { projectSlug = '' } = useUrlState();
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { mutate: deleteJudge } = useDeleteJudge({ projectSlug });

  function handleDelete() {
    deleteJudge(judge.id);
    close();
  }

  return (
    <>
      <Button color="red" variant="light" onClick={toggle}>
        Delete
      </Button>
      <Modal opened={isOpen} centered onClose={close} title="Confirm Judge Deletion">
        <Stack>
          <Stack gap="sm">
            <Text size="sm">Confirm deletion of judge:</Text>
            <Code block>{judge.name}</Code>
            <Text size="sm">
              This will remove all votes from this judge, and recompute leaderboard rankings accordingly. This action
              cannot be undone.
            </Text>
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
