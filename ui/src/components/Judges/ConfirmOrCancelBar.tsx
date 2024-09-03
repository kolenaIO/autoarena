import { Button, ButtonProps, Group } from '@mantine/core';

type Props = {
  onCancel: () => void;
  onConfirm?: () => void;
  action?: string;
  buttonProps?: ButtonProps;
};
export function ConfirmOrCancelBar({ onCancel, onConfirm, action = 'Confirm', buttonProps = {} }: Props) {
  return (
    <Group justify="space-between">
      <Button variant="default" onClick={onCancel} flex={1}>
        Cancel
      </Button>
      <Button onClick={onConfirm} disabled={onConfirm == null} flex={1} {...buttonProps}>
        {action}
      </Button>
    </Group>
  );
}
