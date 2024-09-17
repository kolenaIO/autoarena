import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQuery, useQueryClient, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { getProjectApiUrl } from '../lib/routes.ts';
import { Task } from './useTasks.ts';

function getTaskStreamQueryKey(projectSlug: string, task: Task) {
  return [getProjectApiUrl(projectSlug), '/task', task.id, '/stream'];
}

type Params = {
  projectSlug: string;
  task: Task;
  options?: Partial<UseQueryOptions<Task, Error>>;
};
export function useTaskStream({ projectSlug, task, options = {} }: Params): UseQueryResult<Task, Error> {
  const queryClient = useQueryClient();
  const queryKey = getTaskStreamQueryKey(projectSlug, task);

  return useQuery({
    queryKey,
    queryFn: async ({ signal }) => {
      let latest = task;
      await fetchEventSource(`${getProjectApiUrl(projectSlug)}/task/${task.id}/stream`, {
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
    ...options,
  });
}
