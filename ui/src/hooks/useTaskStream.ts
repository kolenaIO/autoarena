import { useQuery, useQueryClient, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { Task } from './useTasks.ts';
import { useApiFetch } from './useApiFetch.ts';

type Params = {
  projectSlug: string;
  task: Task;
  options?: Partial<UseQueryOptions<Task, Error>>;
};
export function useTaskStream({ projectSlug, task, options = {} }: Params): UseQueryResult<Task, Error> {
  const { apiFetchEventSource } = useApiFetch();
  const queryClient = useQueryClient();
  const url = API_ROUTES.getTaskStream(projectSlug, task.id);
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
    retry: 3,
    ...options,
  });
}
