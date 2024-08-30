import { Button, Group, Modal, Stack, TextInput } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useState } from 'react';
import { useCreateProject } from '../hooks/useCreateProject.ts';

export function CreateNewProject() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { mutate: createProject } = useCreateProject();
  const [name, setName] = useState('');

  return (
    <>
      <Button leftSection={<IconPlus size={18} />} onClick={toggle}>
        Create New Project
      </Button>
      <Modal
        opened={isOpen}
        centered
        onClose={close}
        title="Create Project"
        transitionProps={{ transition: 'fade', duration: 100 }}
      >
        <Stack>
          <TextInput
            label="Project Name"
            placeholder="Enter project name..."
            value={name}
            onChange={event => setName(event.currentTarget.value)}
            flex={1}
          />
          <Group justify="space-between">
            <Button variant="default" onClick={close} flex={1}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                createProject({ name });
                close();
              }}
              disabled={name === ''}
              flex={1}
            >
              Create
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
}
