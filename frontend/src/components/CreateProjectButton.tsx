import { Button, Modal, Stack, TextInput } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useState } from 'react';
import { useCreateProject } from '../hooks/useCreateProject.ts';
import { useProjects } from '../hooks/useProjects.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

export function CreateProjectButton() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { data: projects } = useProjects();
  const { mutate: createProject } = useCreateProject();
  const [name, setName] = useState('');

  const existingProjects = new Set((projects ?? []).map(({ name }) => name));
  const nameError = existingProjects.has(name) ? `Project '${name}' already exists` : undefined;

  function handleClose() {
    setName('');
    close();
  }

  function handleConfirm() {
    createProject({ name });
    handleClose();
  }

  const isDisabled = name === '' || nameError != null;
  return (
    <>
      <Button leftSection={<IconPlus size={18} />} onClick={toggle}>
        Create New Project
      </Button>
      <Modal
        opened={isOpen}
        centered
        onClose={handleClose}
        title="Create Project"
        transitionProps={{ transition: 'fade', duration: 100 }}
      >
        <Stack>
          <TextInput
            label="Project Name"
            placeholder="Enter project name..."
            value={name}
            onChange={event => setName(event.currentTarget.value)}
            error={nameError}
            data-autofocus
            flex={1}
          />
          <ConfirmOrCancelBar
            onCancel={handleClose}
            onConfirm={isDisabled ? undefined : handleConfirm}
            action="Create"
          />
        </Stack>
      </Modal>
    </>
  );
}
