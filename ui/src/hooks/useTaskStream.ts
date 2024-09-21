import { useQuery, useQueryClient, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { Task } from './useTasks.ts';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  task: Task;
  options?: Partial<UseQueryOptions<Task, Error>>;
};
export function useTaskStream({ projectSlug, task, options = {} }: Params): UseQueryResult<Task, Error> {
  const { apiFetchEventSource } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
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
