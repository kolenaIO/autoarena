import { useState } from 'react';
import { Accordion, Button, Checkbox, Collapse, Group, Pill, Stack, Text } from '@mantine/core';
import { Link } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { Judge } from '../../hooks/useJudges.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useUpdateJudge } from '../../hooks/useUpdateJudge.ts';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { judgeTypeIconComponent, judgeTypeToHumanReadableName } from './types.ts';
import { DeleteJudgeButton } from './DeleteJudgeButton.tsx';
import { CanAccessJudgeStatusIndicator } from './CanAccessJudgeStatusIndicator.tsx';

type Props = {
  judge: Judge;
};
export function JudgeAccordionItem({ judge }: Props) {
  const { id, judge_type, name, description, enabled } = judge;
  const { projectSlug = '' } = useUrlState();
  const [isEnabled, setIsEnabled] = useState(enabled);
  const { mutate: updateJudge } = useUpdateJudge({ projectSlug, judgeId: id });
  const [showSystemPrompt, { toggle: toggleShowSystemPrompt }] = useDisclosure(false);

  function handleToggleEnabled() {
    updateJudge({ enabled: !enabled });
    setIsEnabled(prev => !prev);
  }

  const IconComponent = judgeTypeIconComponent(judge_type);
  return (
    <Accordion.Item key={id} value={`${judge_type}-${id}`}>
      <Accordion.Control icon={<IconComponent width={20} height={20} color="var(--mantine-color-gray-8)" />}>
        <Group justify="space-between" pl="xs" pr="lg">
          <Stack gap={0}>
            <Text c={!isEnabled ? 'gray.6' : undefined}>
              {name}{' '}
              {judge_type !== 'human' && (
                <Text span c="dimmed">
                  ({judgeTypeToHumanReadableName(judge_type)})
                </Text>
              )}
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
        <Stack pl="xl" gap="xs">
          <CanAccessJudgeStatusIndicator judgeType={judge_type} />
          {judge_type !== 'human' ? (
            <Group justify="space-between">
              <Checkbox label="Enable as automated judge" checked={isEnabled} onChange={() => handleToggleEnabled()} />
              <Group>
                <Text c="dimmed" size="xs" fs="italic">
                  {judge.votes.toLocaleString()} votes submitted
                </Text>
                <Button variant="light" color="gray" onClick={toggleShowSystemPrompt}>
                  {showSystemPrompt ? 'Hide' : 'Show'} System Prompt
                </Button>
                <DeleteJudgeButton judge={judge} />
              </Group>
            </Group>
          ) : (
            <Text>
              Visit the{' '}
              <Link to={`/project/${projectSlug}/compare`}>
                <Text span c="kolena.8">
                  Head-to-Head
                </Text>
              </Link>{' '}
              tab to provide ratings on head-to-head matchups between models.
            </Text>
          )}
          <Collapse in={showSystemPrompt} fz="sm">
            <MarkdownContent>{`**System Prompt:** ${judge.system_prompt}`}</MarkdownContent>
          </Collapse>
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  );
}
