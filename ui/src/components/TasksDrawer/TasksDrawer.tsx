import { Accordion, Button, Collapse, Drawer, Loader, Stack, Text } from '@mantine/core';
import { IconCactus, IconCpu } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import moment from 'moment';
import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  getTasksQueryKey,
  useTasks,
  useUrlState,
  getModelsQueryKey,
  getJudgesQueryKey,
  useHasActiveTasksStream,
  useClearCompletedTasks,
  useRoutes,
} from '../../hooks';
import { pluralize, taskIsDone } from '../../lib';
import { NonIdealState } from '../NonIdealState.tsx';
import { TaskAccordionItem } from './TaskAccordionItem.tsx';

export function TasksDrawer() {
  const { projectSlug } = useUrlState();
  const { apiRoutes } = useRoutes();
  const [isDrawerOpen, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);
  const queryClient = useQueryClient();
  const [isCompletedTasksOpen, { toggle: toggleCompletedTasks, close: closeCompletedTasks }] = useDisclosure(false);
  const { data: hasActiveTasks = false } = useHasActiveTasksStream(projectSlug);
  const { data: tasks, isLoading: isLoadingTasks } = useTasks({ projectSlug });
  const { mutate: clearCompletedTasks } = useClearCompletedTasks({ projectSlug });

  const tasksSorted = useMemo(() => (tasks ?? []).sort((a, b) => moment(b.created).diff(moment(a.created))), [tasks]);
  const tasksInProgress = useMemo(() => tasksSorted.filter(({ status }) => !taskIsDone(status)), [tasksSorted]);
  const tasksCompleted = useMemo(() => tasksSorted.filter(({ status }) => taskIsDone(status)), [tasksSorted]);

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: getTasksQueryKey(apiRoutes, projectSlug ?? '') });
  }, [isDrawerOpen]);

  // reload models and any related queries if any tasks are newly completed
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: getModelsQueryKey(apiRoutes, projectSlug ?? '') });
    queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(apiRoutes, projectSlug ?? '') });
    // TODO: fix this
    // queryClient.invalidateQueries({ queryKey: [getProjectApiUrl(apiRoutes, projectSlug ?? ''), '/model'] });
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
      <Drawer.Root
        opened={isDrawerOpen}
        onClose={() => {
          closeDrawer();
          closeCompletedTasks();
        }}
        position="right"
        size="xl"
        transitionProps={{ duration: 200 }}
      >
        <Drawer.Overlay />
        <Drawer.Content>
          <Drawer.Header>
            <Drawer.Title>
              <Text fs="italic" c="dimmed" size="sm">
                {tasksInProgress.length > 0
                  ? `Showing ${pluralize(tasksInProgress.length, 'active task')}`
                  : 'No active tasks'}
              </Text>
            </Drawer.Title>
            <Drawer.CloseButton />
          </Drawer.Header>
          <Drawer.Body flex={1} h="calc(100% - 60px)" /* full height minus header */>
            {tasksSorted.length < 1 && !isLoadingTasks ? (
              <Stack justify="center" h="100%">
                <NonIdealState IconComponent={IconCactus} description="No tasks to show" />
              </Stack>
            ) : (
              <Stack pb="md">
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
            )}
          </Drawer.Body>
        </Drawer.Content>
      </Drawer.Root>
    </>
  );
}
