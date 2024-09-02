import { Anchor, Code, Modal, Select, Stack, Text } from '@mantine/core';
import { useMemo, useState } from 'react';
import moment from 'moment';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useProjects } from '../../hooks/useProjects.ts';
import { pluralize } from '../../lib/string.ts';
import { useModels } from '../../hooks/useModels.ts';
import { useCreateFineTuningTask } from '../../hooks/useCreateFineTuningTask.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';

const AVAILABLE_BASE_MODELS = ['gemma2:9b', 'gemma2:2b', 'llama3.1:8b'];

type Props = {
  isOpen: boolean;
  onClose: () => void;
};
export function CreateFineTunedJudgeModal({ isOpen, onClose }: Props) {
  const { projectId = -1 } = useUrlState();
  const { data: projects } = useProjects();
  const { data: models } = useModels(projectId);
  const { mutate: createFineTuningTask } = useCreateFineTuningTask({ projectId });
  const project = useMemo(() => (projects ?? []).find(({ id }) => id === projectId), [projects, projectId]);
  const [baseModel, setBaseModel] = useState<string | null>(null);

  const nVotes = useMemo(() => (models ?? []).reduce((acc, x) => acc + x.votes, 0) / 2, [models]);

  function handleClose() {
    setBaseModel(null);
    onClose();
  }

  function handleSubmit() {
    if (baseModel != null) {
      createFineTuningTask({ base_model: baseModel });
    }
    handleClose();
  }

  const isEnabled = baseModel != null;
  return (
    <Modal
      opened={isOpen}
      onClose={handleClose}
      centered
      title="Create Custom Fine-Tuned Judge"
      transitionProps={{ transition: 'fade', duration: 100 }} // TODO: share these
    >
      <Stack>
        <Text size="sm">
          Start a <b>fine-tuning job</b> to create a custom judge model using the {pluralize(nVotes, 'manual vote')}{' '}
          submitted on the <Anchor href={`/project/${projectId}/compare`}>Head-to-Head</Anchor> tab within the{' '}
          <Code>{project?.name}</Code> project.
        </Text>
        <Select
          label="Base Model"
          placeholder="Select Base Model"
          data={AVAILABLE_BASE_MODELS}
          value={baseModel}
          onChange={newModel => setBaseModel(newModel)}
          searchable
          flex={1}
        />
        <Text size="sm">
          <b>Estimated Training Time:</b>{' '}
          {baseModel != null ? (
            moment.duration(estimateTrainingTime(baseModel, nVotes), 'seconds').humanize()
          ) : (
            <Text span c="dimmed" fs="italic">
              Select Base Model
            </Text>
          )}
        </Text>
        <Text size="sm">
          You can view progress in the 'Tasks' menu and download or run the fine-tuned model when the task completes.
        </Text>
        <ConfirmOrCancelBar onCancel={handleClose} onConfirm={isEnabled ? handleSubmit : undefined} action="Create" />
      </Stack>
    </Modal>
  );
}

// TODO this is a dirty hack
function estimateTrainingTime(baseModel: string, nDatapoints: number) {
  const nEpochs = 3;
  const estimateSecs = 0.5 * nDatapoints * nEpochs;
  if (baseModel === 'gemma2:2b') {
    return estimateSecs / 4;
  }
  return estimateSecs;
}
