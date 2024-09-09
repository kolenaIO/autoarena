import {
  Button,
  Code,
  FileInput,
  Modal,
  TextInput,
  Text,
  Stack,
  ButtonVariant,
  MantineSize,
  Group,
} from '@mantine/core';
import { IconCheck, IconPlus, IconX } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useMemo, useState } from 'react';
import { useUploadModelResponses } from '../hooks/useUploadModelResponses.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useModels } from '../hooks/useModels.ts';
import { useJudges } from '../hooks/useJudges.ts';
import { pluralize } from '../lib/string.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';
import { isEnabledAutoJudge } from './Judges/utils.ts';

type Props = {
  variant?: ButtonVariant;
  size?: MantineSize;
};
export function AddModelButton({ variant, size }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: models } = useModels(projectSlug);
  const { data: judges } = useJudges(projectSlug);
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { mutate: uploadModelResponses } = useUploadModelResponses({ projectSlug });

  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');

  const existingModelNames = useMemo(() => new Set((models ?? []).map(({ name }) => name)), [models]);
  const nameError = existingModelNames.has(name) ? `Model '${name}' already exists` : undefined;

  const configuredAutoJudges = useMemo(() => (judges ?? []).filter(isEnabledAutoJudge), [judges]);

  function handleClose() {
    setFile(null);
    setName('');
    close();
  }

  function handleSubmit() {
    if (file != null) {
      uploadModelResponses([file, name]);
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
            label="Model Responses File"
            description={
              <Text inherit>
                A <Code>.csv</Code> file containing <Code>prompt</Code> and <Code>response</Code> columns
              </Text>
            }
            placeholder="Select file with model responses..."
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
          <Group gap="xs" wrap="nowrap">
            {configuredAutoJudges.length > 0 ? <IconCheck size={18} color="green" /> : <IconX size={18} color="gray" />}
            <Text size="xs">
              <Stack gap={2}>
                <Text inherit>
                  {configuredAutoJudges.length > 0
                    ? `${pluralize(configuredAutoJudges.length, 'automated judge')} configured`
                    : 'No automated judges configured'}
                </Text>
                <Text inherit c="dimmed">
                  {configuredAutoJudges.length > 0
                    ? 'Model will be ranked against existing models on leaderboard'
                    : 'Configure an automated judge to rank against existing models'}
                </Text>
              </Stack>
            </Text>
          </Group>
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
