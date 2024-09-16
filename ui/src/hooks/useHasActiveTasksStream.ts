import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQuery, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';

function getHasActiveTasksQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/tasks', '/has-active'];
}

export function useHasActiveTasksStream(projectSlug?: string): UseQueryResult<boolean, Error> {
  const queryClient = useQueryClient();
  const queryKey = getHasActiveTasksQueryKey(projectSlug ?? '');

  return useQuery({
    queryKey,
    queryFn: async ({ signal }) => {
      await fetchEventSource(`${getProjectUrl(projectSlug ?? '')}/tasks/has-active`, {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
        signal,
        onmessage: event => {
          const parsedData: { has_active: boolean } = JSON.parse(event.data);
          queryClient.setQueryData(queryKey, parsedData.has_active);
        },
      });
      return false; // shouldn't get here
    },
    enabled: projectSlug != null,
  });
}
