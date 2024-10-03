import { useState } from 'react';
import { Accordion, Button, Checkbox, Collapse, Group, Loader, Pill, Stack, Text, Tooltip } from '@mantine/core';
import { Link } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { IconDownload, IconGavel, IconPrompt } from '@tabler/icons-react';
import { Judge, useUpdateJudge, useUrlState, useDownloadFile, useAppRoutes } from '../../hooks';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { pluralize } from '../../lib';
import {
  DEFAULT_HUMAN_JUDGE_NAME,
  isDefaultHumanJudge,
  judgeTypeIconComponent,
  judgeTypeToHumanReadableName,
} from './types.ts';
import { DeleteJudgeButton } from './DeleteJudgeButton.tsx';
import { CanAccessJudgeStatusIndicator } from './CanAccessJudgeStatusIndicator.tsx';
import { TriggerAutoJudgeModal } from './TriggerAutoJudgeModal.tsx';

type Props = {
  judge: Judge;
};
export function JudgeAccordionItem({ judge }: Props) {
  const { id, judge_type, name, description, enabled } = judge;
  const { projectSlug = '' } = useUrlState();
  const { apiRoutes, appRoutes } = useAppRoutes();
  const [isEnabled, setIsEnabled] = useState(enabled);
  const { mutate: updateJudge } = useUpdateJudge({ projectSlug, judgeId: id });
  const [showSystemPrompt, { toggle: toggleShowSystemPrompt }] = useDisclosure(false);
  const [showAutoJudgeModal, { toggle: toggleShowAutoJudgeModal, close: closeShowAutoJudgeModal }] =
    useDisclosure(false);
  const { mutate: downloadVotes, isPending: isDownloadingVotes } = useDownloadFile(
    apiRoutes.downloadJudgeVotesCsv(projectSlug, judge.id),
    `${judge.name}-judge-votes.csv`
  );

  function handleToggleEnabled() {
    updateJudge({ enabled: !enabled });
    setIsEnabled(prev => !prev);
  }

  const canDownload = judge.n_votes > 0;
  const DownloadVotesComponent = (
    <Button
      variant="light"
      color="teal"
      size="xs"
      leftSection={isDownloadingVotes ? <Loader color="teal" size={20} /> : <IconDownload size={20} />}
      disabled={!canDownload}
      onClick={() => downloadVotes()}
    >
      Download Votes CSV
    </Button>
  );
  const IconComponent = judgeTypeIconComponent(judge_type);
  return (
    <Accordion.Item key={id} value={`${judge_type}-${id}`}>
      <Accordion.Control
        icon={
          <IconComponent
            size={20}
            color={isEnabled ? 'var(--mantine-color-black)' : 'var(--mantine-color-gray-light-color)'}
          />
        }
      >
        <Group justify="space-between" pl="xs" pr="lg">
          <Stack gap={0}>
            <Text c={!isEnabled ? 'gray.6' : undefined}>
              {isDefaultHumanJudge(judge) ? (
                judgeTypeToHumanReadableName(judge_type)
              ) : (
                <>
                  {name}{' '}
                  <Text span c="dimmed">
                    ({judgeTypeToHumanReadableName(judge_type)})
                  </Text>
                </>
              )}
            </Text>
            <Text c="dimmed" size="xs">
              {description}
            </Text>
          </Stack>
          <Group>
            <Text c="dimmed" size="xs" fs="italic">
              {pluralize(judge.n_votes, 'vote')}
            </Text>
            {isEnabled ? (
              <Pill bg="ice.0" c="ice.9">
                Enabled
              </Pill>
            ) : (
              <Pill c="gray">Disabled</Pill>
            )}
          </Group>
        </Group>
      </Accordion.Control>
      <Accordion.Panel>
        <Stack pl="xl" gap="xs">
          {judge_type !== 'human' ? (
            <>
              <CanAccessJudgeStatusIndicator judgeType={judge_type} />
              <Group justify="space-between">
                <Checkbox
                  label="Enable as automated judge"
                  checked={isEnabled}
                  onChange={() => handleToggleEnabled()}
                />
                <Group>
                  <Button
                    variant="light"
                    color="gray"
                    size="xs"
                    leftSection={<IconPrompt size={20} />}
                    onClick={toggleShowSystemPrompt}
                  >
                    {showSystemPrompt ? 'Hide' : 'Show'} System Prompt
                  </Button>
                  {DownloadVotesComponent}
                  <Tooltip label="Judge must be enabled" disabled={judge.enabled}>
                    <Button
                      variant="light"
                      color="orange"
                      size="xs"
                      leftSection={<IconGavel size={20} />}
                      onClick={toggleShowAutoJudgeModal}
                      disabled={!judge.enabled}
                    >
                      Run Automated Judgement
                    </Button>
                  </Tooltip>
                  <DeleteJudgeButton judge={judge} />
                  <TriggerAutoJudgeModal
                    judgeId={judge.id}
                    isOpen={showAutoJudgeModal}
                    onClose={closeShowAutoJudgeModal}
                  />
                </Group>
              </Group>
            </>
          ) : (
            <Group justify="space-between">
              <Text size="sm">
                Visit the{' '}
                <Link
                  to={appRoutes.compare(projectSlug)}
                  style={{ textDecoration: 'none', color: 'var(--mantine-color-kolena-light-color)' }}
                >
                  Head-to-Head
                </Link>{' '}
                tab to provide ratings on head-to-head matchups between models.
              </Text>
              {DownloadVotesComponent}
              {!isDefaultHumanJudge(judge) && <DeleteJudgeButton judge={judge} />}
            </Group>
          )}
          <Collapse in={showSystemPrompt} fz="sm">
            <MarkdownContent>{`**System Prompt:** ${judge.system_prompt}`}</MarkdownContent>
          </Collapse>
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  );
}
