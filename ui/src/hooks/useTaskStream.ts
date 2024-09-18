import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQuery, useQueryClient, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { Task } from './useTasks.ts';

type Params = {
  projectSlug: string;
  task: Task;
  options?: Partial<UseQueryOptions<Task, Error>>;
};
export function useTaskStream({ projectSlug, task, options = {} }: Params): UseQueryResult<Task, Error> {
  const queryClient = useQueryClient();
  const url = API_ROUTES.getTaskStream(projectSlug, task.id);
  const queryKey = urlAsQueryKey(url);

  // TODO: bearer token
  return useQuery({
    queryKey,
    queryFn: async ({ signal }) => {
      let latest = task;
      await fetchEventSource(url, {
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
