import { Code, Modal, Stack, TextInput, Text, Anchor } from '@mantine/core';
import { useState } from 'react';
import { useCreateJudge } from '../../hooks/useCreateJudge.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';
import { JudgeType } from './types.ts';

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
      judge_type: 'ollama' as JudgeType, // TODO: annoying to have to cast this, should probably set up enum
      name,
      description: `Ollama judge running model '${name}' locally`,
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
        <Stack gap={0}>
          <Text size="sm">
            Enter a model name to use as a judge that runs locally via Ollama. You can specify any model that can be
            downloaded from <Anchor href="https://ollama.com/library">Ollama</Anchor>. Some examples include:
          </Text>
          <ul>
            <li>
              <Code>llama3.1:8b</Code>
            </li>
            <li>
              <Code>gemma2:9b</Code>
            </li>
            <li>
              <Code>mistral-nemo:12b</Code>
            </li>
          </ul>
        </Stack>
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
