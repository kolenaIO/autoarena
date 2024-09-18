import moment from 'moment/moment';
import { IconBooks, IconCalculator, IconGavel } from '@tabler/icons-react';
import { Accordion, Badge, Button, Code, Group, Progress, Stack, Text } from '@mantine/core';
import { useMemo, useState } from 'react';
import { Task } from '../../hooks/useTasks.ts';
import { taskIsDone, taskStatusToColor, taskStatusToLabel } from '../../lib/tasks.ts';
import { useTaskStream } from '../../hooks/useTaskStream.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';

const N_LOG_LINES_DEFAULT = 30;

type Props = {
  task: Task;
};
export function TaskAccordionItem({ task: inputTask }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: task = inputTask } = useTaskStream({
    projectSlug,
    task: inputTask,
    options: { enabled: !taskIsDone(inputTask.status) },
  });
  const [showFullLogs, setShowFullLogs] = useState(false);

  const slug = `${task.task_type}-${moment(task.created).format('YYYYMMDD-hhmmss-SSS')}`;
  const IconComponent =
    task.task_type === 'recompute-leaderboard'
      ? IconCalculator
      : task.task_type === 'auto-judge'
        ? IconGavel
        : IconBooks;
  const taskTitle =
    task.task_type === 'recompute-leaderboard'
      ? 'Recompute Leaderboard Rankings'
      : task.task_type === 'auto-judge'
        ? 'Automated Head-to-Head Judging'
        : 'Custom Judge Fine-Tuning';
  const iconColor =
    task.task_type === 'recompute-leaderboard'
      ? 'var(--mantine-color-blue-6)'
      : task.task_type === 'auto-judge'
        ? 'var(--mantine-color-orange-6)'
        : 'var(--mantine-color-green-6)';

  const [startLogs, endLogs]: [string[], string[]] = useMemo(() => {
    const logLines = task.logs.split('\n');
    if (showFullLogs || logLines.length <= N_LOG_LINES_DEFAULT) {
      return [logLines, []];
    }
    const halfLines = N_LOG_LINES_DEFAULT / 2;
    return [logLines.slice(0, halfLines), logLines.slice(logLines.length - halfLines, logLines.length)];
  }, [task.logs, showFullLogs]);

  return (
    <Accordion.Item value={slug}>
      <Accordion.Control icon={<IconComponent size={24} color={iconColor} />}>
        <Group justify="space-between" pr="md">
          <Stack gap={0}>
            <Text>{taskTitle}</Text>
            <Text size="xs" c="dimmed">
              {moment(task.created).format('YYYY-MM-DD (hh:mm A)')}
            </Text>
          </Stack>
          <Badge variant="light" color={taskStatusToColor(task.status)}>
            {taskStatusToLabel(task.status)}
          </Badge>
        </Group>
      </Accordion.Control>
      <Accordion.Panel>
        <Stack>
          <Progress
            color={`${taskStatusToColor(task.status)}.2`}
            value={task.progress * 100}
            striped={!taskIsDone(task.status)}
            animated={!taskIsDone(task.status)}
          />
          <Code block fs="xs">
            {startLogs.map((line, i) => (
              <LogLine key={i} line={line} />
            ))}
            {endLogs.length > 0 && (
              <>
                <Button color="gray" variant="subtle" size="xs" m={8} onClick={() => setShowFullLogs(true)}>
                  Show full logs
                </Button>
                {endLogs.map((line, i) => (
                  <LogLine key={`end-${i}`} line={line} />
                ))}
              </>
            )}
          </Code>
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  );
}

function LogLine({ line }: { line: string }) {
  return (
    <Text inherit>
      <Text span inherit c="dimmed">
        {line.slice(0, 21)}
      </Text>
      <Text span inherit>
        {line.slice(21, line.length)}
      </Text>
    </Text>
  );
}
