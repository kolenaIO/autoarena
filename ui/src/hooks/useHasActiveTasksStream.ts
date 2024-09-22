import { useQuery, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useAppRoutes } from './useAppRoutes.ts';

export function useHasActiveTasksStream(projectSlug?: string): UseQueryResult<boolean, Error> {
  const { apiFetchEventSource } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.getHasActiveTasksStream(projectSlug ?? '');
  const queryKey = urlAsQueryKey(url);

  // TODO: auth header
  return useQuery({
    queryKey,
    queryFn: async ({ signal }) => {
      await apiFetchEventSource(url, {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
        signal,
        onmessage: event => {
          const parsedData: { has_active: boolean } = JSON.parse(event.data);
          queryClient.setQueryData(queryKey, parsedData.has_active);
        },
        onerror: () => {
          throw new Error('Failed to fetch active task stream'); // without this, fetchEventSource retries indefinitely
        },
      });
      return false; // shouldn't get here
    },
    enabled: projectSlug != null,
  });
}
