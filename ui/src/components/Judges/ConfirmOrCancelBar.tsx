import { Button, ButtonProps, Group, Tooltip } from '@mantine/core';
import { ReactNode } from 'react';

type Props = {
  onCancel: () => void;
  onConfirm?: () => void;
  action?: string;
  confirmButtonProps?: ButtonProps;
  disabledTooltipLabel?: ReactNode;
};
export function ConfirmOrCancelBar({
  onCancel,
  onConfirm,
  action = 'Confirm',
  confirmButtonProps = {},
  disabledTooltipLabel,
}: Props) {
  const isDisabled = onConfirm == null;
  const ConfirmButtonComponent = (
    <Button onClick={onConfirm} disabled={isDisabled} flex={1} {...confirmButtonProps}>
      {action}
    </Button>
  );
  return (
    <Group justify="space-between">
      <Button variant="default" onClick={onCancel} flex={1}>
        Cancel
      </Button>
      {disabledTooltipLabel != null && isDisabled ? (
        <Tooltip openDelay={200} label={disabledTooltipLabel}>
          {ConfirmButtonComponent}
        </Tooltip>
      ) : (
        ConfirmButtonComponent
      )}
    </Group>
  );
}
