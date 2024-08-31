import { useState } from 'react';
import { Code, Modal, Select, Stack, Text } from '@mantine/core';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useCreateJudge } from '../../hooks/useCreateJudge.ts';
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
  const { mutate: createJudge } = useCreateJudge({ projectId });
  const [name, setName] = useState('');

  function handleSubmit() {
    createJudge({
      project_id: projectId,
      judge_type: judgeType,
      name,
      description: `${judgeTypeToHumanReadableName(judgeType)} judge model '${name}' called via API`, // TODO
    });
    onClose();
  }

  const isEnabled = name !== '';
  const apiKeyName = judgeTypeToApiKeyName(judgeType);
  return (
    <Modal
      opened={isOpen}
      onClose={onClose}
      centered
      title={`Create ${judgeTypeToHumanReadableName(judgeType)} Judge`}
      transitionProps={{ transition: 'fade', duration: 100 }} // TODO: share these
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
          data={modelOptions}
          value={name}
          onChange={setName}
          searchable
          flex={1}
        />
        <ConfirmOrCancelBar onCancel={onClose} onConfirm={isEnabled ? handleSubmit : undefined} action="Create" />
      </Stack>
    </Modal>
  );
}
