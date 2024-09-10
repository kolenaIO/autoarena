import { useMemo, useState } from 'react';
import { Code, Modal, Select, Stack, Text } from '@mantine/core';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useCreateJudge } from '../../hooks/useCreateJudge.ts';
import { useJudges } from '../../hooks/useJudges.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';
import { ConfigureSystemPromptCollapse } from './ConfigureSystemPromptCollapse.tsx';
import { CanAccessJudgeStatusIndicator } from './CanAccessJudgeStatusIndicator.tsx';
import { JudgeType } from './types.ts';

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function CreatePythonExtensionJudgeModal({ isOpen, onClose }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: judges } = useJudges(projectSlug);
  const { mutate: createJudge } = useCreateJudge({ projectSlug });
  const [name, setName] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');

  const modelOptions = ['myjudge.MyJudge'];

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
      judge_type: 'python' as JudgeType,
      name,
      model_name: name,
      system_prompt: systemPrompt,
      description: `Custom judge model '${name}' called via API`,
    });
    handleClose();
  }

  const isEnabled = name !== '';
  return (
    <Modal opened={isOpen} onClose={handleClose} centered title={<Text fw={500}>Create Python Extension Judge</Text>}>
      <Stack fz="sm">
        <Text inherit>Use a custom Python extension as a judge.</Text>
        <Text inherit>
          To define an extension, implement the <Code>CustomJudge</Code> interface and pass an{' '}
          <Code>--extensions myjudge.MyJudge</Code> flag with the path to your implementation when running AutoArena.
        </Text>
        <Select
          label="Model Name"
          placeholder="Select Model"
          data={availableModels}
          value={name}
          onChange={newName => setName(newName ?? '')}
          searchable
          flex={1}
        />
        <ConfigureSystemPromptCollapse value={systemPrompt} setValue={setSystemPrompt} />
        <CanAccessJudgeStatusIndicator judgeType="custom" />
        <ConfirmOrCancelBar onCancel={handleClose} onConfirm={isEnabled ? handleSubmit : undefined} action="Create" />
      </Stack>
    </Modal>
  );
}
