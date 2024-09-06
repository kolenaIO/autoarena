import { ReactNode, useMemo, useState } from 'react';
import { Code, Modal, Select, Stack, Text, TextInput } from '@mantine/core';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useCreateJudge } from '../../hooks/useCreateJudge.ts';
import { useJudges } from '../../hooks/useJudges.ts';
import { JudgeType, judgeTypeToApiKeyName, judgeTypeToHumanReadableName } from './types.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';
import { ConfigureSystemPromptCollapse } from './ConfigureSystemPromptCollapse.tsx';

type Props = {
  judgeType: JudgeType;
  modelOptions?: string[];
  isOpen: boolean;
  onClose: () => void;
  extraCopy?: ReactNode;
};
export function CreateProprietaryJudgeModal({ judgeType, modelOptions, isOpen, onClose, extraCopy }: Props) {
  const { projectId = -1 } = useUrlState();
  const { data: judges } = useJudges(projectId);
  const { mutate: createJudge } = useCreateJudge({ projectId });
  const [name, setName] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');

  // gray out options that are already configured
  const existingJudges = useMemo(() => new Set((judges ?? []).map(({ name }) => name)), [judges]);
  const availableModels = useMemo(
    () => (modelOptions ?? []).map(name => ({ value: name, label: name, disabled: existingJudges.has(name) })),
    [modelOptions, existingJudges]
  );

  function handleClose() {
    setName('');
    onClose();
  }

  function handleSubmit() {
    createJudge({
      project_id: projectId,
      judge_type: judgeType,
      name,
      model_name: name,
      system_prompt: systemPrompt,
      description: `${judgeTypeToHumanReadableName(judgeType)} judge model '${name}' called via API`,
    });
    handleClose();
  }

  const isEnabled = name !== '';
  const apiKeyName = judgeTypeToApiKeyName(judgeType);
  return (
    <Modal
      opened={isOpen}
      onClose={handleClose}
      centered
      title={<Text fw={500}>Create {judgeTypeToHumanReadableName(judgeType)} Judge</Text>}
    >
      <Stack fz="sm" gap="xs">
        <Text inherit>Call the {judgeTypeToHumanReadableName(judgeType)} API as a judge.</Text>
        {apiKeyName != null && (
          <Text inherit>
            Requires a valid <Code>{apiKeyName}</Code> in the environment running AutoArena.
          </Text>
        )}
        {extraCopy}
        {modelOptions != null ? (
          <Select
            label="Model Name"
            placeholder="Select Model"
            data={availableModels}
            value={name}
            onChange={newName => setName(newName ?? '')}
            searchable
            flex={1}
          />
        ) : (
          <TextInput
            label="Model Name"
            placeholder="Enter model name"
            value={name}
            onChange={event => setName(event.currentTarget.value)}
            flex={1}
          />
        )}
        <ConfigureSystemPromptCollapse value={systemPrompt} setValue={setSystemPrompt} />
        <ConfirmOrCancelBar onCancel={handleClose} onConfirm={isEnabled ? handleSubmit : undefined} action="Create" />
      </Stack>
    </Modal>
  );
}
