import { Collapse, Group, Stack, Text, Textarea, UnstyledButton } from '@mantine/core';
import { IconChevronDown, IconChevronUp } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useEffect } from 'react';

type Props = {
  value: string;
  setValue: (prompt: string) => void;
};
export function ConfigureSystemPromptCollapse({ value, setValue }: Props) {
  const [isOpen, { toggle }] = useDisclosure(false);

  // TODO: the backend should control the default system prompt
  useEffect(() => {
    setValue(
      `You are a human preference judge tasked with deciding which of the two assistant responses, A or B, better responds to the user's prompt.

Respond with ONLY "A" if assistant A is better, "B" if assistant B is better, or "-" if neither is better than the other.`
    );
  }, []);

  const chevronProps = { size: 18, color: 'gray' };
  return (
    <Stack gap={2}>
      <UnstyledButton onClick={toggle}>
        <Group justify="space-between">
          <Stack gap={2}>
            <Text fw={500} size="sm">
              Configure System Prompt
            </Text>
            <Text size="xs" c="dimmed">
              Customize the instructions given to the judge before voting
            </Text>
          </Stack>
          {isOpen ? <IconChevronUp {...chevronProps} /> : <IconChevronDown {...chevronProps} />}
        </Group>
      </UnstyledButton>
      <Collapse in={isOpen}>
        <Textarea rows={8} value={value} setValue={setValue} />
      </Collapse>
    </Stack>
  );
}
