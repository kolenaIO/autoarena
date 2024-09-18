import { useQuery } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';

export function useHeadToHeadCount(projectSlug?: string) {
  const url = API_ROUTES.getHeadToHeadCount(projectSlug ?? '');
  return useQuery({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch head-to-head count');
      }
      const result: number = await response.json();
      return result;
    },
    enabled: projectSlug != null,
  });
}
