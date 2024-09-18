import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQuery, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';

export function useHasActiveTasksStream(projectSlug?: string): UseQueryResult<boolean, Error> {
  const queryClient = useQueryClient();
  const url = API_ROUTES.getHasActiveTasksStream(projectSlug ?? '');
  const queryKey = urlAsQueryKey(url);

  // TODO: auth header
  return useQuery({
    queryKey,
    queryFn: async ({ signal }) => {
      await fetchEventSource(url, {
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
