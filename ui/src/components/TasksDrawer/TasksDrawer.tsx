import { Accordion, Button, Collapse, Drawer, Loader, Stack, Text } from '@mantine/core';
import { IconCpu } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import moment from 'moment';
import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getTasksQueryKey, useTasks } from '../../hooks/useTasks.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { pluralize } from '../../lib/string.ts';
import { getModelsQueryKey } from '../../hooks/useModels.ts';
import { useClearCompletedTasks } from '../../hooks/useClearCompletedTasks.ts';
import { taskIsDone } from '../../lib/tasks.ts/utils.ts';
import { getProjectUrl } from '../../lib/routes.ts';
import { getJudgesQueryKey } from '../../hooks/useJudges.ts';
import { useHasActiveTasksStream } from '../../hooks/useHasActiveTasksStream.ts';
import { TaskAccordionItem } from './TaskAccordionItem.tsx';

export function TasksDrawer() {
  const { projectSlug } = useUrlState();
  const [isDrawerOpen, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);
  const queryClient = useQueryClient();
  const [isCompletedTasksOpen, { toggle: toggleCompletedTasks, close: closeCompletedTasks }] = useDisclosure(false);
  const { data: hasActiveTasks } = useHasActiveTasksStream(projectSlug);
  const { data: tasks } = useTasks({ projectSlug });
  const { mutate: clearCompletedTasks } = useClearCompletedTasks({ projectSlug });

  const tasksSorted = useMemo(() => (tasks ?? []).sort((a, b) => moment(b.created).diff(moment(a.created))), [tasks]);
  const tasksInProgress = useMemo(() => tasksSorted.filter(({ status }) => !taskIsDone(status)), [tasksSorted]);
  const tasksCompleted = useMemo(() => tasksSorted.filter(({ status }) => taskIsDone(status)), [tasksSorted]);

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectSlug ?? '') });
  }, [isDrawerOpen]);

  // reload models and any related queries if any tasks are newly completed
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectSlug ?? '') });
    queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectSlug ?? '') });
    queryClient.invalidateQueries({ queryKey: [getProjectUrl(projectSlug ?? ''), '/model'] });
  }, [tasksCompleted.length]);

  return (
    <>
      <Button
        variant="light"
        onClick={toggleDrawer}
        leftSection={
          hasActiveTasks ? (
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
        size="xl"
        transitionProps={{ duration: 200 }}
        title={
          <Text fs="italic" c="dimmed" size="sm">
            {tasksInProgress.length > 0
              ? `Showing ${pluralize(tasksInProgress.length, 'active task')}`
              : 'No active tasks'}
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
                <Stack>
                  <Accordion>
                    {tasksCompleted.map((task, i) => (
                      <TaskAccordionItem key={i} task={task} />
                    ))}
                  </Accordion>
                  <Button variant="light" color="red" onClick={() => clearCompletedTasks()}>
                    Clear Completed Tasks
                  </Button>
                </Stack>
              </Collapse>
            </>
          )}
        </Stack>
      </Drawer>
    </>
  );
}
