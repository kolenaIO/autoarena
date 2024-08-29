import { Accordion, Button, Center, Group, Pill, Stack, Text } from '@mantine/core';
import { ReactNode } from 'react';
import { IconBrandMeta, IconBrandOpenai, IconPlus, IconRobot, IconUsers } from '@tabler/icons-react';

type Judge = {
  id: string;
  label: string;
  description: string;
  icon: ReactNode;
  enabled?: boolean;
  custom?: boolean;
};
const JUDGE_ICON_PROPS = { width: 20, height: 20, color: 'var(--mantine-color-gray-8)' };
export const JUDGES: Judge[] = [
  {
    id: 'human-ratings',
    label: 'Human Ratings',
    description: "Manual ratings submitted via the 'Head-to-Head' tab",
    icon: <IconUsers {...JUDGE_ICON_PROPS} />,
    enabled: true,
  },
  {
    id: 'custom-giga-gorilla-20240828',
    label: 'Giga Gorilla (2024/08/28)',
    description: 'Custom judge model fine-tuned using 2,491 of your ratings submitted on AutoStack',
    icon: <IconRobot {...JUDGE_ICON_PROPS} />,
    enabled: true,
    custom: true,
  },
  {
    id: 'gpt-4o',
    label: 'GPT-4o',
    description: 'Full-featured, best-in-class frontier model from OpenAI',
    icon: <IconBrandOpenai {...JUDGE_ICON_PROPS} />,
  },
  {
    id: 'gpt-4o-mini',
    label: 'GPT-4o mini',
    description: 'Cost-effective and low-latency frontier model from OpenAI',
    icon: <IconBrandOpenai {...JUDGE_ICON_PROPS} />,
    enabled: true,
  },
  {
    id: 'llama-3.1-70b',
    label: 'Llama3.1 70B',
    description: 'Capable open-source model from Meta and run by AutoStack',
    icon: <IconBrandMeta {...JUDGE_ICON_PROPS} />,
  },
  {
    id: 'llama-3.1-8b',
    label: 'Llama3.1 8B',
    description: 'Faster and less capable open-source model from Meta and run by AutoStack',
    icon: <IconBrandMeta {...JUDGE_ICON_PROPS} />,
  },
];

export function Judges() {
  return (
    <Center p="lg">
      <Stack>
        <Accordion variant="contained" w={1080}>
          {JUDGES.map(({ id, label, description, icon, enabled = false, custom = false }) => (
            <Accordion.Item key={id} value={id}>
              <Accordion.Control icon={icon}>
                <Group justify="space-between" pl="xs" pr="lg">
                  <Stack gap={0}>
                    <Text>{label}</Text>
                    <Text c="dimmed" size="xs">
                      {description}
                    </Text>
                  </Stack>
                  <Group>
                    {custom && (
                      <Pill bg="kolena.1" c="gray.8">
                        Custom
                      </Pill>
                    )}
                    {enabled && (
                      <Pill bg="ice.0" c="gray.8">
                        Enabled
                      </Pill>
                    )}
                  </Group>
                </Group>
              </Accordion.Control>
              <Accordion.Panel>{description}</Accordion.Panel>
            </Accordion.Item>
          ))}
        </Accordion>
        <Center>
          <Button leftSection={<IconPlus size={18} />}>Create Custom Judge</Button>
        </Center>
      </Stack>
    </Center>
  );
}
