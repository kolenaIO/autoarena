import { Button, Group } from '@mantine/core';

type Props = {
  onCancel: () => void;
  onConfirm?: () => void;
  action?: string;
};
export function ConfirmOrCancelBar({ onCancel, onConfirm, action = 'Confirm' }: Props) {
  return (
    <Group justify="space-between">
      <Button variant="default" onClick={onCancel} flex={1}>
        Cancel
      </Button>
      <Button onClick={onConfirm} disabled={onConfirm == null} flex={1}>
        {action}
      </Button>
    </Group>
  );
}
