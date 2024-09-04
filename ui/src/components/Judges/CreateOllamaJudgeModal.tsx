import { Code, Modal, Stack, TextInput, Text, Anchor } from '@mantine/core';
import { useMemo, useState } from 'react';
import { useCreateJudge } from '../../hooks/useCreateJudge.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useJudges } from '../../hooks/useJudges.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';
import { JudgeType } from './types.ts';
import { ConfigureSystemPromptCollapse } from './ConfigureSystemPromptCollapse.tsx';

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function CreateOllamaJudgeModal({ isOpen, onClose }: Props) {
  const { projectId = -1 } = useUrlState();
  const { data: judges } = useJudges(projectId);
  const { mutate: createJudge } = useCreateJudge({ projectId });
  const [name, setName] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');

  const existingJudges = useMemo(() => new Set((judges ?? []).map(({ name }) => name)), [judges]);
  const nameError = existingJudges.has(name) ? `Model '${name}' already configured as judge` : undefined;

  function handleClose() {
    setName('');
    onClose();
  }

  function handleSubmit() {
    const judgeType: JudgeType = 'ollama';
    createJudge({
      project_id: projectId,
      judge_type: judgeType,
      name,
      model_name: name,
      system_prompt: systemPrompt,
      description: `Ollama judge running model '${name}' locally`,
    });
    handleClose();
  }

  const isEnabled = name !== '' && nameError == null;
  return (
    <Modal opened={isOpen} onClose={handleClose} centered title="Create Ollama Judge">
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
          <Text size="sm">
            Note that this model must be pulled via <Code>ollama pull</Code> and the Ollama service must be running on
            the host running AutoStack.
          </Text>
        </Stack>
        <TextInput
          label="Model Name"
          placeholder="Enter model name, e.g. 'gemma2:9b'..."
          value={name}
          onChange={event => setName(event.currentTarget.value)}
          error={nameError}
          flex={1}
        />
        <ConfigureSystemPromptCollapse value={systemPrompt} setValue={setSystemPrompt} />
        <ConfirmOrCancelBar onCancel={handleClose} onConfirm={isEnabled ? handleSubmit : undefined} action="Create" />
      </Stack>
    </Modal>
  );
}
