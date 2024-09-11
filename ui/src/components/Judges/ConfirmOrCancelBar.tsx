import { Button, ButtonProps, Group, Tooltip } from '@mantine/core';
import { ReactNode } from 'react';

type Props = {
  onCancel: () => void;
  onConfirm?: () => void;
  action?: string;
  submitForm?: boolean;
  confirmButtonProps?: ButtonProps;
  disabledTooltipLabel?: ReactNode;
};
export function ConfirmOrCancelBar({
  onCancel,
  onConfirm,
  action = 'Confirm',
  submitForm = false,
  confirmButtonProps = {},
  disabledTooltipLabel,
}: Props) {
  const isDisabled = onConfirm == null && !submitForm;
  const ConfirmButtonComponent = (
    <Button
      type={submitForm ? 'submit' : undefined}
      onClick={onConfirm}
      disabled={isDisabled}
      flex={1}
      {...confirmButtonProps}
    >
      {action}
    </Button>
  );
  return (
    <Group justify="space-between">
      <Button variant="default" onClick={onCancel} flex={1}>
        Cancel
      </Button>
      {disabledTooltipLabel != null && isDisabled ? (
        <Tooltip label={disabledTooltipLabel}>{ConfirmButtonComponent}</Tooltip>
      ) : (
        ConfirmButtonComponent
      )}
    </Group>
  );
}
