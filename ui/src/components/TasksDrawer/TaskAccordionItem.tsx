import moment from 'moment/moment';
import { IconBooks, IconCalculator, IconGavel } from '@tabler/icons-react';
import { Accordion, Badge, Code, Group, Progress, Stack, Text } from '@mantine/core';
import { Task } from '../../hooks/useTasks.ts';
import { taskIsDone, taskStatusToColor, taskStatusToLabel } from '../../lib/tasks.ts';
import { useTaskStream } from '../../hooks/useTaskStream.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';

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
            {task.logs.split('\n').map((line, i) => (
              <Text inherit key={i}>
                <Text span inherit c="dimmed">
                  {line.slice(0, 21)}
                </Text>
                <Text span inherit>
                  {line.slice(21, line.length)}
                </Text>
              </Text>
            ))}
          </Code>
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  );
}
