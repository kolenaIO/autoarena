import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQuery, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';
import { Task } from './useTasks.ts';

function getTaskStreamQueryKey(projectSlug: string, task: Task) {
  return [getProjectUrl(projectSlug), '/task', task.id, '/stream'];
}

export function useTaskStream(projectSlug: string, task: Task, enabled: boolean): UseQueryResult<Task, Error> {
  const queryClient = useQueryClient();
  const queryKey = getTaskStreamQueryKey(projectSlug, task);

  return useQuery({
    queryKey,
    queryFn: async ({ signal }) => {
      let latest = task;
      await fetchEventSource(`${getProjectUrl(projectSlug)}/task/${task.id}/stream`, {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
        signal,
        onmessage: event => {
          const parsedData: Task = JSON.parse(event.data);
          latest = parsedData;
          queryClient.setQueryData(queryKey, parsedData);
        },
      });
      return latest;
    },
    initialData: task,
    enabled,
  });
}
