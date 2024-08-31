import { Accordion, Center, Checkbox, Divider, Group, Pill, SimpleGrid, Stack, Text, Title } from '@mantine/core';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { Judge, useJudges } from '../../hooks/useJudges.ts';
import { useUpdateJudge } from '../../hooks/useUpdateJudge.ts';
import { ConfigureJudgeCard } from './ConfigureJudgeCard.tsx';
import { judgeTypeIconComponent, judgeTypeToHumanReadableName } from './types.ts';

export function Judges() {
  const { projectId } = useUrlState();
  const { data: judges } = useJudges(projectId);
  return (
    <Center p="lg">
      <Stack>
        <Title order={5}>Configured Judges</Title>
        <Accordion variant="contained" w={1080}>
          {(judges ?? []).map(judge => (
            <JudgeAccordionItem key={judge.id} judge={judge} />
          ))}
        </Accordion>

        <Divider />

        <Title order={5}>Configure New Judge</Title>
        <SimpleGrid cols={3} w={1080}>
          <ConfigureJudgeCard judgeType="ollama" description="Configure any local Ollama model as a judge" />
          <ConfigureJudgeCard
            judgeType="openai"
            description="Configure an OpenAI model like GPT-4o or GPT-4o mini as a judge"
          />
          <ConfigureJudgeCard judgeType="custom" description="Fine-tune a custom judge model on AutoStack" />
          <ConfigureJudgeCard judgeType="gemini" description="Configure a Google Gemini model as a judge" />
          <ConfigureJudgeCard
            judgeType="anthropic"
            description="Configure an Anthropic model like Claude 3.5 Sonnet or Claude 3 Opus as a judge"
          />
          <ConfigureJudgeCard
            judgeType="cohere"
            description="Configure Command R or Command R+ from Cohere as a judge"
          />
        </SimpleGrid>
      </Stack>
    </Center>
  );
}

export function JudgeAccordionItem({ judge: { id, judge_type, name, description, enabled } }: { judge: Judge }) {
  const { projectId = -1 } = useUrlState();
  const [isEnabled, setIsEnabled] = useState(enabled);
  const { mutate: updateJudge } = useUpdateJudge({ projectId });

  function handleToggleEnabled() {
    updateJudge({ project_id: projectId, judge_id: id, enabled: !enabled });
    setIsEnabled(prev => !prev);
  }

  const IconComponent = judgeTypeIconComponent(judge_type);
  return (
    <Accordion.Item key={id} value={`${judge_type}-${id}`}>
      <Accordion.Control icon={<IconComponent width={20} height={20} color="var(--mantine-color-gray-8)" />}>
        <Group justify="space-between" pl="xs" pr="lg">
          <Stack gap={0}>
            <Text c={!isEnabled ? 'gray.6' : undefined}>
              {name} {judge_type !== 'human' && `(${judgeTypeToHumanReadableName(judge_type)})`}
            </Text>
            <Text c="dimmed" size="xs">
              {description}
            </Text>
          </Stack>
          <Group>
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
          {judge_type !== 'human' ? (
            <Checkbox label="Enable as automated judge" checked={isEnabled} onChange={() => handleToggleEnabled()} />
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
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  );
}
