import { Accordion, Badge, Button, Code, Collapse, Drawer, Group, Loader, Progress, Stack, Text } from '@mantine/core';
import { IconBooks, IconCalculator, IconCpu, IconGavel } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import moment from 'moment';
import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Task, useTasks } from '../hooks/useTasks.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { pluralize } from '../lib/string.ts';
import { getModelsQueryKey } from '../hooks/useModels.ts';

export function TasksDrawer() {
  const { projectId } = useUrlState();
  const [isDrawerOpen, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);
  const queryClient = useQueryClient();
  const [isCompletedTasksOpen, { toggle: toggleCompletedTasks, close: closeCompletedTasks }] = useDisclosure(false);
  const { data: tasks } = useTasks({
    projectId,
    options: { refetchInterval: isDrawerOpen ? 1_000 : 10_000 }, // TODO: polling this every 10 seconds on the app isn't great
  });
  const tasksSorted = useMemo(() => (tasks ?? []).sort((a, b) => moment(b.created).diff(moment(a.created))), [tasks]);
  const tasksInProgress = useMemo(() => tasksSorted.filter(({ progress }) => progress < 1), [tasksSorted]);
  const tasksCompleted = useMemo(() => tasksSorted.filter(({ progress }) => progress >= 1), [tasksSorted]);

  // reload models if any tasks are newly completed
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectId ?? -1) });
  }, [tasksCompleted.length]);

  return (
    <>
      <Button
        variant="light"
        onClick={toggleDrawer}
        leftSection={
          tasksInProgress.length > 0 ? (
            <Loader size={18} type="bars" />
          ) : (
            <IconCpu width={20} height={20} color="var(--mantine-color-kolena-8)" />
          )
        }
      >
        Tasks
      </Button>
      <Drawer
        opened={isDrawerOpen}
        onClose={() => {
          closeDrawer();
          closeCompletedTasks();
        }}
        position="right"
        size="lg"
        transitionProps={{ duration: 200 }}
        title={
          <Text fs="italic" c="dimmed" size="sm">
            {tasksInProgress.length > 0
              ? `Showing ${pluralize(tasksInProgress.length, 'in-progress task')}`
              : 'No in-progress tasks'}
          </Text>
        }
      >
        <Stack>
          <Accordion>
            {tasksInProgress.map((task, i) => (
              <TaskAccordionItem key={i} task={task} />
            ))}
          </Accordion>
          {tasksCompleted.length > 0 && (
            <>
              <Button variant="light" color="gray" onClick={toggleCompletedTasks}>
                {isCompletedTasksOpen ? 'Hide' : 'Show'} {pluralize(tasksCompleted.length, 'completed task')}
              </Button>
              <Collapse in={isCompletedTasksOpen}>
                <Accordion>
                  {tasksCompleted.map((task, i) => (
                    <TaskAccordionItem key={i} task={task} />
                  ))}
                </Accordion>
              </Collapse>
            </>
          )}
        </Stack>
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
      ? 'Recompute Leaderboard Rankings'
      : task.task_type === 'auto-judge'
        ? 'Automated Head-to-Head Judging'
        : 'Custom Judge Fine-Tuning';
  const iconColor =
    task.task_type === 'recompute-confidence-intervals'
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
          <Badge variant="light" color={task.progress < 1 ? 'cyan' : 'gray'}>
            {task.progress < 1 ? 'In Progress' : 'Complete'}
          </Badge>
        </Group>
      </Accordion.Control>
      <Accordion.Panel>
        <Stack>
          <Progress value={task.progress * 100} striped={task.progress < 1} animated={task.progress < 1} />
          <Code block fs="xs">
            {task.status}
          </Code>
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  );
}
