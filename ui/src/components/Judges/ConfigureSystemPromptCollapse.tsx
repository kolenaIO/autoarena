import { Collapse, Group, Stack, Text, Textarea, UnstyledButton } from '@mantine/core';
import { IconChevronDown, IconChevronUp } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useEffect } from 'react';
import { useJudgeDefaultSystemPrompt, useUrlState } from '../../hooks';

type Props = {
  value: string;
  setValue: (prompt: string) => void;
};
export function ConfigureSystemPromptCollapse({ value, setValue }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: defaultSystemPrompt } = useJudgeDefaultSystemPrompt(projectSlug);
  const [isOpen, { toggle }] = useDisclosure(false);

  useEffect(() => {
    if (defaultSystemPrompt != null) {
      setValue(defaultSystemPrompt);
    }
  }, [defaultSystemPrompt]);

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
        <Textarea rows={8} value={value} onChange={event => setValue(event.currentTarget.value)} />
      </Collapse>
    </Stack>
  );
}
