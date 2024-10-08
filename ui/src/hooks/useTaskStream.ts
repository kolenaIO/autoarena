import { useQuery, useQueryClient, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { Task } from './useTasks.ts';
import { useAppRoutes } from './useAppRoutes.ts';

type Params = {
  projectSlug: string;
  task: Task;
  options?: Partial<UseQueryOptions<Task, Error>>;
};
export function useTaskStream({ projectSlug, task, options = {} }: Params): UseQueryResult<Task, Error> {
  const { apiFetchEventSource } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.getTaskStream(projectSlug, task.id);
  const queryKey = urlAsQueryKey(url);

  return useQuery({
    queryKey,
    queryFn: async ({ signal }) => {
      let latest = task;
      await apiFetchEventSource(url, {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
        signal,
        onmessage: event => {
          const parsedData: Task = JSON.parse(event.data);
          latest = parsedData;
          queryClient.setQueryData(queryKey, parsedData);
        },
        onerror: () => {
          throw new Error('Failed to fetch task stream');
        },
      });
      return latest;
    },
    initialData: task,
    ...options,
  });
}
