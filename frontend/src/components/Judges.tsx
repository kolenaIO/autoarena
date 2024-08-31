import { Accordion, Button, Center, Checkbox, Group, PasswordInput, Pill, Stack, Text, Title } from '@mantine/core';
import { ReactNode, useState } from 'react';
import {
  IconBrandGoogleFilled,
  IconBrandMeta,
  IconBrandOpenai,
  IconDevices2,
  IconPlus,
  IconRobot,
  IconUsers,
} from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useJudges } from '../hooks/useJudges.ts';

type Judge = {
  id: string;
  label: string;
  description: string;
  icon: ReactNode;
  enabled?: boolean;
  custom?: boolean;
  thirdParty?: boolean;
  fineTuningDetails?: { [key: string]: string };
};
const JUDGE_ICON_PROPS = { width: 20, height: 20, color: 'var(--mantine-color-gray-8)' };
const HUMAN_JUDGE: Judge = {
  id: 'human-ratings',
  label: 'Human',
  description: "Manual ratings submitted via the 'Head-to-Head' tab. Always enabled.",
  icon: <IconUsers {...JUDGE_ICON_PROPS} />,
  enabled: true,
};
const JUDGES: Judge[] = [
  HUMAN_JUDGE,
  {
    id: 'custom-vengeful-hare-20240826',
    label: 'Vengeful Hare (2024/08/26)',
    description: 'Custom judge model fine-tuned using 742 of your ratings submitted on AutoStack',
    icon: <IconRobot {...JUDGE_ICON_PROPS} />,
    custom: true,
  },
  {
    id: 'custom-giga-gorilla-20240828',
    label: 'Giga Gorilla (2024/08/28)',
    description: 'Custom judge model fine-tuned using 2,491 of your ratings submitted on AutoStack',
    icon: <IconRobot {...JUDGE_ICON_PROPS} />,
    custom: true,
  },
  {
    id: 'gpt-4o',
    label: 'GPT-4o',
    description: 'Full-featured, best-in-class frontier model from OpenAI',
    icon: <IconBrandOpenai {...JUDGE_ICON_PROPS} />,
    thirdParty: true,
  },
  {
    id: 'gpt-4o-mini',
    label: 'GPT-4o mini',
    description: 'Cost-effective and low-latency frontier model from OpenAI',
    icon: <IconBrandOpenai {...JUDGE_ICON_PROPS} />,
    enabled: true,
    thirdParty: true,
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
  {
    id: 'gemini-1.5-pro',
    label: 'Gemini 1.5 Pro',
    description: 'Highly competitive frontier model from Google',
    icon: <IconBrandGoogleFilled {...JUDGE_ICON_PROPS} />,
    thirdParty: true,
  },
  {
    id: 'ollama-local',
    label: 'Ollama (local)',
    description: 'Any model runnable locally with Ollama',
    icon: <IconDevices2 {...JUDGE_ICON_PROPS} />,
  },
];

export function Judges() {
  const { projectId } = useUrlState();
  const { data: judges } = useJudges(projectId);
  return (
    <Center p="lg">
      <Stack>
        {JSON.stringify(judges)}
        <Title order={4}>Enabled Judges</Title>
        <Text>Enabled judge</Text>
        <Accordion variant="contained" w={1080}>
          {[HUMAN_JUDGE].map(judge => (
            <JudgeAccordionItem key={judge.id} judge={judge} />
          ))}
        </Accordion>

        <Accordion variant="contained" w={1080}>
          {JUDGES.slice(1, JUDGES.length).map(judge => (
            <JudgeAccordionItem key={judge.id} judge={judge} />
          ))}
        </Accordion>
        <Center>
          <Button leftSection={<IconPlus size={18} />}>Create Custom Judge</Button>
        </Center>
      </Stack>
    </Center>
  );
}

export function JudgeAccordionItem({
  judge: { id, icon, label, description, enabled, custom, thirdParty },
}: {
  judge: Judge;
}) {
  const [isEnabled, setIsEnabled] = useState(enabled);
  return (
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
            {thirdParty && (
              <Pill bg="orange.1" c="gray.8">
                3rd Party
              </Pill>
            )}
            {isEnabled && (
              <Pill bg="ice.0" c="gray.8">
                Enabled
              </Pill>
            )}
          </Group>
        </Group>
      </Accordion.Control>
      <Accordion.Panel>
        <Stack pl="xl">
          {id !== HUMAN_JUDGE.id ? (
            <Checkbox
              label="Enable as automated judge"
              checked={isEnabled}
              onChange={() => setIsEnabled(prev => !prev)}
            />
          ) : (
            <Text>
              Visit the{' '}
              <Link to="/compare">
                <Text span c="kolena.8">
                  Head-to-Head
                </Text>
              </Link>{' '}
              tab to provide ratings on head-to-head matchups between models.
            </Text>
          )}
          {thirdParty && (
            <Group align="flex-end" justify="space-between" w="100%">
              <PasswordInput label="API Key" placeholder="Enter API key" flex={1} />
              <Button variant="light">Save</Button>
            </Group>
          )}
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  );
}
