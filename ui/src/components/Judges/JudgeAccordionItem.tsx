import { useState } from 'react';
import { Accordion, Button, Checkbox, Collapse, Group, Loader, Pill, Stack, Text, Tooltip } from '@mantine/core';
import { Link } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { IconDownload, IconGavel, IconPrompt } from '@tabler/icons-react';
import { Judge } from '../../hooks/useJudges.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useUpdateJudge } from '../../hooks/useUpdateJudge.ts';
import { MarkdownContent } from '../MarkdownContent.tsx';
import { pluralize } from '../../lib/string.ts';
import { API_ROUTES } from '../../lib/routes.ts';
import { useDownloadFile } from '../../hooks/useDownloadFile.ts';
import { judgeTypeIconComponent, judgeTypeToHumanReadableName } from './types.ts';
import { DeleteJudgeButton } from './DeleteJudgeButton.tsx';
import { CanAccessJudgeStatusIndicator } from './CanAccessJudgeStatusIndicator.tsx';
import { TriggerAutoJudgeModal } from './TriggerAutoJudgeModal.tsx';

type Props = {
  judge: Judge;
};
export function JudgeAccordionItem({ judge }: Props) {
  const { id, judge_type, name, description, enabled } = judge;
  const { projectSlug = '' } = useUrlState();
  const [isEnabled, setIsEnabled] = useState(enabled);
  const { mutate: updateJudge } = useUpdateJudge({ projectSlug, judgeId: id });
  const [showSystemPrompt, { toggle: toggleShowSystemPrompt }] = useDisclosure(false);
  const [showAutoJudgeModal, { toggle: toggleShowAutoJudgeModal, close: closeShowAutoJudgeModal }] =
    useDisclosure(false);
  const { mutate: downloadVotes, isPending: isDownloadingVotes } = useDownloadFile(
    API_ROUTES.downloadJudgeVotesCsv(projectSlug, judge.id),
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
      <Accordion.Control icon={<IconComponent width={20} height={20} color="var(--mantine-color-gray-8)" />}>
        <Group justify="space-between" pl="xs" pr="lg">
          <Stack gap={0}>
            <Text c={!isEnabled ? 'gray.6' : undefined}>
              {judge_type !== 'human' ? (
                <>
                  {name}{' '}
                  <Text span c="dimmed">
                    ({judgeTypeToHumanReadableName(judge_type)})
                  </Text>
                </>
              ) : (
                'Human'
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
                <Link to={`/project/${projectSlug}/compare`}>
                  <Text span c="kolena.8">
                    Head-to-Head
                  </Text>
                </Link>{' '}
                tab to provide ratings on head-to-head matchups between models.
              </Text>
              {DownloadVotesComponent}
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
