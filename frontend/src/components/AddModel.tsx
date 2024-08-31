import { Button, Code, FileInput, Modal, TextInput, Text, Stack, ButtonVariant } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useState } from 'react';
import { useUploadModelResults } from '../hooks/useUploadModelResults.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

type Props = {
  variant?: ButtonVariant;
};
export function AddModel({ variant }: Props) {
  const { projectId = -1 } = useUrlState(); // TODO: handle unset state?
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { mutate: uploadModelResults } = useUploadModelResults({ projectId });

  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');

  function handleSubmit() {
    if (file != null) {
      uploadModelResults([file, name]);
    }
    close();
  }

  const isDisabled = file == null || name === '';
  return (
    <>
      <Button variant={variant} leftSection={<IconPlus size={18} />} onClick={toggle}>
        Add Model
      </Button>
      <Modal
        opened={isOpen}
        centered
        onClose={close}
        title="Add Model" // TODO: better title?
        transitionProps={{ transition: 'fade', duration: 100 }} // TODO: share these
      >
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
            flex={1}
          />
          <ConfirmOrCancelBar onCancel={close} onConfirm={isDisabled ? undefined : handleSubmit} action="Upload" />
        </Stack>
      </Modal>
    </>
  );
}
