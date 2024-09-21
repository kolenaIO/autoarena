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
  Transition,
  CloseButton,
} from '@mantine/core';
import { IconCheck, IconPlus, IconX } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useMemo, useState } from 'react';
import { useUploadModelResponses, useUrlState, useModels, useJudges } from '../hooks';
import { pluralize } from '../lib';
import { ConfirmOrCancelBar, isEnabledAutoJudge } from './Judges';

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

  const [files, setFiles] = useState<File[]>([]);
  const [names, setNames] = useState<string[]>([]);

  const existingModelNames = useMemo(() => new Set((models ?? []).map(({ name }) => name)), [models]);
  const nameErrors = names.map(name => {
    if (existingModelNames.has(name)) {
      return `Model '${name}' already exists`;
    }
    if (names.filter(n => n === name).length > 1) {
      return `Duplicate model name '${name}'`;
    }
  });

  const configuredAutoJudges = useMemo(() => (judges ?? []).filter(isEnabledAutoJudge), [judges]);

  function handleClose() {
    setFiles([]);
    setNames([]);
    close();
  }

  function handleSubmit() {
    if (files.length > 0) {
      uploadModelResponses([files, names]);
    }
    handleClose();
  }

  function handleRemove(i: number) {
    return () => {
      setFiles(prev => prev.filter((_, j) => i !== j));
      setNames(prev => prev.filter((_, j) => i !== j));
    };
  }

  const hasEmptyNames = names.some(name => name === '');
  const isDisabled = files.length === 0 || hasEmptyNames || nameErrors.some(e => e != null);
  return (
    <>
      <Button variant={variant} size={size} leftSection={<IconPlus size={18} />} onClick={toggle}>
        Add Model
      </Button>
      <Modal opened={isOpen} centered onClose={handleClose} title="Add Model Responses">
        <Stack>
          <FileInput<true>
            label="Model Responses File"
            description={
              <Text inherit>
                One or more <Code>.csv</Code> files containing <Code>prompt</Code> and <Code>response</Code> columns
              </Text>
            }
            placeholder="Select file with model responses..."
            accept="text/csv"
            value={files}
            multiple
            onChange={(f: File[]) => {
              setFiles(f);
              setNames(f.map(file => file.name.slice(0, -4)));
            }}
          />
          <Transition mounted={files.length > 0} transition="slide-right" duration={200} timingFunction="ease">
            {transitionStyle => (
              <Stack style={transitionStyle}>
                {files.map((file, i) => (
                  <Group gap="xs" align="flex-start">
                    <TextInput
                      key={i}
                      label={
                        <Text size="sm" fw={500}>
                          Model Name for <Code>{file.name}</Code>
                        </Text>
                      }
                      placeholder={`Enter name for '${file.name}'...`}
                      value={names[i]}
                      onChange={event =>
                        setNames(prev => {
                          // not sure why currentTarget is sometimes missing
                          const newName = event.currentTarget?.value ?? event.target?.value ?? '';
                          return [...prev.slice(0, i), newName, ...prev.slice(i + 1, prev.length)];
                        })
                      }
                      error={nameErrors[i]}
                      flex={1}
                    />
                    <CloseButton mt="xl" size="sm" onClick={handleRemove(i)} />
                  </Group>
                ))}
              </Stack>
            )}
          </Transition>
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
                    ? `Model${files.length > 0 ? 's' : ''} will be ranked against existing models on leaderboard`
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
