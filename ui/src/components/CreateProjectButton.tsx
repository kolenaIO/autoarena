import { ActionIcon, Button, MantineSize, Modal, Stack, TextInput } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { useCreateProject, useProjects } from '../hooks';
import { ConfirmOrCancelBar } from './Judges';

type Form = {
  name: string;
};
type Props = {
  size?: MantineSize;
  small?: boolean;
};
export function CreateProjectButton({ size, small }: Props) {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { data: projects } = useProjects();
  const { mutate: createProject } = useCreateProject();

  const form = useForm<Form>({
    mode: 'uncontrolled',
    initialValues: { name: '' },
    validate: { name: validateName },
    validateInputOnChange: true,
  });

  function validateName(name: string) {
    const existingProjects = new Set((projects ?? []).map(({ slug }) => slug));
    return name === ''
      ? 'Name cannot be empty'
      : existingProjects.has(name)
        ? `Project '${name}' already exists`
        : undefined;
  }

  function handleClose() {
    form.reset();
    close();
  }

  function handleSubmit({ name }: Form) {
    createProject({ name });
    handleClose();
  }

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
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            <TextInput
              label="Project Name"
              placeholder="Enter project name..."
              data-autofocus
              flex={1}
              key={form.key('name')}
              {...form.getInputProps('name')}
            />
            <ConfirmOrCancelBar onCancel={handleClose} submitForm={form.isValid()} action="Create" />
          </Stack>
        </form>
      </Modal>
    </>
  );
}
