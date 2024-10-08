import { urlAsQueryKey, useAppConfig } from '../lib';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { useAppRoutes } from './useAppRoutes.ts';

export type Model = {
  id: number;
  name: string;
  created: string;
  elo: number;
  q025?: number; // these are only set once models have been rated
  q975?: number;
  n_responses: number;
  n_votes: number;
};

export function useModels(projectSlug: string | undefined) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.getModels(projectSlug ?? '');
  return useQueryWithErrorToast({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch models');
      }
      const result: Model[] = await response.json();
      return result;
    },
    enabled: projectSlug != null,
    errorMessage: 'Failed to fetch models',
  });
}
