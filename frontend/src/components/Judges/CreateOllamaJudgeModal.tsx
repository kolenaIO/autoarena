import { Modal, Stack, TextInput } from '@mantine/core';
import { useState } from 'react';
import { useCreateJudge } from '../../hooks/useCreateJudge.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function CreateOllamaJudgeModal({ isOpen, onClose }: Props) {
  const { projectId = -1 } = useUrlState();
  const { mutate: createJudge } = useCreateJudge({ projectId });
  const [name, setName] = useState('');

  function handleSubmit() {
    createJudge({
      project_id: projectId,
      judge_type: 'ollama',
      name,
      description: '', // TODO: ???
    });
    onClose();
  }

  const isEnabled = name !== '';
  return (
    <Modal
      opened={isOpen}
      onClose={onClose}
      centered
      title="Create Ollama Judge"
      transitionProps={{ transition: 'fade', duration: 100 }} // TODO: share these
    >
      <Stack>
        <TextInput
          label="Model Name"
          placeholder="Enter model name, e.g. 'gemma2:9b'..."
          value={name}
          onChange={event => setName(event.currentTarget.value)}
          flex={1}
        />
        <ConfirmOrCancelBar onCancel={onClose} onConfirm={isEnabled ? handleSubmit : undefined} action="Create" />
      </Stack>
    </Modal>
  );
}
