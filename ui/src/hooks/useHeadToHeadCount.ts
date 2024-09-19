import { useQuery } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { useApiFetch } from './useApiFetch.ts';

export function useHeadToHeadCount(projectSlug?: string) {
  const { apiFetch } = useApiFetch();
  const url = API_ROUTES.getHeadToHeadCount(projectSlug ?? '');
  return useQuery({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch head-to-head count');
      }
      const result: number = await response.json();
      return result;
    },
    enabled: projectSlug != null,
  });
}
