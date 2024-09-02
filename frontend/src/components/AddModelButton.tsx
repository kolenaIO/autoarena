import { Button, Code, FileInput, Modal, TextInput, Text, Stack, ButtonVariant, MantineSize } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useMemo, useState } from 'react';
import { useUploadModelResults } from '../hooks/useUploadModelResults.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useModels } from '../hooks/useModels.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

type Props = {
  variant?: ButtonVariant;
  size?: MantineSize;
};
export function AddModelButton({ variant, size }: Props) {
  const { projectId = -1 } = useUrlState();
  const { data: models } = useModels(projectId);
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { mutate: uploadModelResults } = useUploadModelResults({ projectId });

  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');

  const existingModelNames = useMemo(() => new Set((models ?? []).map(({ name }) => name)), [models]);
  const nameError = existingModelNames.has(name) ? `Model '${name}' already exists` : undefined;

  function handleClose() {
    setFile(null);
    setName('');
    close();
  }

  function handleSubmit() {
    if (file != null) {
      uploadModelResults([file, name]);
    }
    handleClose();
  }

  const isDisabled = file == null || name === '' || nameError != null;
  return (
    <>
      <Button variant={variant} size={size} leftSection={<IconPlus size={18} />} onClick={toggle}>
        Add Model
      </Button>
      <Modal opened={isOpen} centered onClose={handleClose} title="Add Model">
        <Stack>
          <FileInput
            label="Model Results"
            description={
              <Text inherit>
                A <Code>.csv</Code> file containing <Code>prompt</Code> and <Code>response</Code> columns
              </Text>
            }
            placeholder="Select model results file..."
            accept="text/csv"
            value={file}
            onChange={f => {
              if (f != null && name == '') {
                setName(f.name.slice(0, -4));
              }
              setFile(f);
            }}
          />
          <TextInput
            label="Model Name"
            placeholder="Enter model name..."
            value={name}
            onChange={event => setName(event.currentTarget.value)}
            error={nameError}
            flex={1}
          />
          <ConfirmOrCancelBar
            onCancel={handleClose}
            onConfirm={isDisabled ? undefined : handleSubmit}
            action="Upload"
          />
        </Stack>
      </Modal>
    </>
  );
}
