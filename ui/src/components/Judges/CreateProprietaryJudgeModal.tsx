import { useMemo, useState } from 'react';
import { Code, Collapse, Group, Modal, Select, Stack, Text, Textarea, UnstyledButton } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconChevronDown, IconChevronUp } from '@tabler/icons-react';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useCreateJudge } from '../../hooks/useCreateJudge.ts';
import { useJudges } from '../../hooks/useJudges.ts';
import { JudgeType, judgeTypeToApiKeyName, judgeTypeToHumanReadableName } from './types.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';

type Props = {
  judgeType: JudgeType;
  modelOptions: string[];
  isOpen: boolean;
  onClose: () => void;
};
export function CreateProprietaryJudgeModal({ judgeType, modelOptions, isOpen, onClose }: Props) {
  const { projectId = -1 } = useUrlState();
  const { data: judges } = useJudges(projectId);
  const { mutate: createJudge } = useCreateJudge({ projectId });
  const [name, setName] = useState('');
  const [isConfigureSystemPromptOpen, { toggle: toggleConfigureSystemPrompt }] = useDisclosure(false);

  // gray out options that are already configured
  const existingJudges = useMemo(() => new Set((judges ?? []).map(({ name }) => name)), [judges]);
  const availableModels = useMemo(
    () => modelOptions.map(name => ({ value: name, label: name, disabled: existingJudges.has(name) })),
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
      description: `${judgeTypeToHumanReadableName(judgeType)} judge model '${name}' called via API`,
    });
    handleClose();
  }

  const isEnabled = name !== '';
  const apiKeyName = judgeTypeToApiKeyName(judgeType);
  const chevronProps = { size: 18, color: 'gray' };
  return (
    <Modal
      opened={isOpen}
      onClose={handleClose}
      centered
      title={`Create ${judgeTypeToHumanReadableName(judgeType)} Judge`}
    >
      <Stack>
        <Text size="sm">Call the {judgeTypeToHumanReadableName(judgeType)} API as a judge.</Text>
        {apiKeyName != null && (
          <Text size="sm">
            Requires a valid <Code>{apiKeyName}</Code> in the environment running AutoStack.
          </Text>
        )}
        <Select
          label="Model Name"
          placeholder="Select Model"
          data={availableModels}
          value={name}
          onChange={newName => setName(newName ?? '')}
          searchable
          flex={1}
        />
        <Stack gap={2}>
          <UnstyledButton onClick={toggleConfigureSystemPrompt}>
            <Group justify="space-between">
              <Stack gap={2}>
                <Text fw={500} size="sm">
                  Configure System Prompt
                </Text>
                <Text size="xs" c="dimmed">
                  Customize the instructions given to the judge before voting
                </Text>
              </Stack>
              {isConfigureSystemPromptOpen ? (
                <IconChevronUp {...chevronProps} />
              ) : (
                <IconChevronDown {...chevronProps} />
              )}
            </Group>
          </UnstyledButton>
          <Collapse in={isConfigureSystemPromptOpen}>
            <Textarea
              rows={8}
              defaultValue={`You are a human preference judge tasked with deciding which of the two assistant responses, A or B, better responds to the user's prompt.

Respond with ONLY "A" if assistant A is better, "B" if assistant B is better, or "-" if neither is better than the other.`}
            />
          </Collapse>
        </Stack>
        <ConfirmOrCancelBar onCancel={handleClose} onConfirm={isEnabled ? handleSubmit : undefined} action="Create" />
      </Stack>
    </Modal>
  );
}
