import { useQuery } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useRoutes } from './useRoutes.ts';

export function useHeadToHeadCount(projectSlug?: string) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useRoutes();
  const url = apiRoutes.getHeadToHeadCount(projectSlug ?? '');
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
