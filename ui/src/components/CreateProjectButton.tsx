import { ActionIcon, Button, MantineSize, Modal, Stack, TextInput } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { useCreateProject } from '../hooks/useCreateProject.ts';
import { useProjects } from '../hooks/useProjects.ts';
import { ConfirmOrCancelBar } from './Judges/ConfirmOrCancelBar.tsx';

type Props = {
  size?: MantineSize;
  small?: boolean;
};
export function CreateProjectButton({ size, small }: Props) {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { data: projects } = useProjects();
  const { mutate: createProject } = useCreateProject();

  const existingProjects = new Set((projects ?? []).map(({ slug }) => slug));
  const form = useForm<{ name: string }>({
    mode: 'uncontrolled',
    initialValues: { name: '' },
    validate: { name: name => (existingProjects.has(name) ? `Project '${name}' already exists` : undefined) },
    validateInputOnChange: true,
  });

  function handleClose() {
    close();
  }

  function handleConfirm(name: string) {
    createProject({ name });
    handleClose();
  }

  const isDisabled = form.getValues().name === '' || !form.isValid;
  return (
    <>
      {small ? (
        <ActionIcon variant="default" onClick={toggle}>
          <IconPlus size={14} />
        </ActionIcon>
      ) : (
        <Button size={size} leftSection={<IconPlus size={18} />} onClick={toggle}>
          Create Project
        </Button>
      )}
      <Modal opened={isOpen} centered onClose={handleClose} title="Create Project">
        <form onSubmit={form.onSubmit(({ name }) => handleConfirm(name))}>
          <Stack>
            <TextInput
              label="Project Name"
              placeholder="Enter project name..."
              data-autofocus
              flex={1}
              key={form.key('name')}
              {...form.getInputProps('name')}
            />
            <ConfirmOrCancelBar onCancel={handleClose} submitForm={!isDisabled} action="Create" />
          </Stack>
        </form>
      </Modal>
    </>
  );
}
