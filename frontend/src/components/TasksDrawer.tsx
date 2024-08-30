import { Accordion, Button, Drawer, Stack, Text } from '@mantine/core';
import { IconBooks, IconCalculator, IconCpu, IconGavel } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import moment from 'moment';
import { useMemo } from 'react';
import { Task, useTasks } from '../hooks/useTasks.ts';
import { useUrlState } from '../hooks/useUrlState.ts';

export function TasksDrawer() {
  const { projectId } = useUrlState();
  const [isOpen, { toggle, close }] = useDisclosure(false);
  const { data: tasks } = useTasks(projectId);
  const tasksSorted = useMemo(() => (tasks ?? []).sort((a, b) => moment(b.created).diff(moment(a.created))), [tasks]);
  return (
    <>
      <Button
        variant="light"
        onClick={toggle}
        leftSection={<IconCpu width={20} height={20} color="var(--mantine-color-kolena-8)" />}
      >
        Tasks
      </Button>
      <Drawer
        opened={isOpen}
        onClose={close}
        position="right"
        transitionProps={{ duration: 200 }}
        title={
          <Text fs="italic" c="dimmed" size="sm">
            Showing {tasksSorted.length.toLocaleString()} task{tasksSorted.length > 1 && 's'}
          </Text>
        }
      >
        <Accordion>
          {(tasks ?? []).map((task, i) => (
            <TaskAccordionItem key={i} task={task} />
          ))}
        </Accordion>
      </Drawer>
    </>
  );
}

function TaskAccordionItem({ task }: { task: Task }) {
  const slug = `${task.task_type}-${moment(task.created).format('YYYYMMDD-hhmmss-SSS')}`;
  const IconComponent =
    task.task_type === 'recompute-confidence-intervals'
      ? IconCalculator
      : task.task_type === 'auto-judge'
        ? IconGavel
        : IconBooks;
  const taskTitle =
    task.task_type === 'recompute-confidence-intervals'
      ? 'Recompute Confidence Intervals'
      : task.task_type === 'auto-judge'
        ? 'Automated Head-to-Head Judging'
        : 'Custom Judge Fine-Tuning';
  return (
    <Accordion.Item value={slug}>
      <Accordion.Control icon={<IconComponent size={24} color="var(--mantine-color-gray-8)" />}>
        <Stack gap={0}>
          <Text>{taskTitle}</Text>
          <Text size="xs" c="dimmed">
            {moment(task.created).format('YYYY-MM-DD (hh:mm A)')}
          </Text>
        </Stack>
      </Accordion.Control>
      <Accordion.Panel>{task.status}</Accordion.Panel>
    </Accordion.Item>
  );
}
