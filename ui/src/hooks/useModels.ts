import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { useRoutes } from './useRoutes.ts';

export function getModelsQueryKey(apiRoutes: ReturnType<useRoutes>['apiRoutes'], projectSlug: string) {
  return urlAsQueryKey(apiRoutes.getModels(projectSlug));
}

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
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const url = apiRoutes.getModels(projectSlug ?? '');
  return useQueryWithErrorToast({
    queryKey: getModelsQueryKey(apiRoutes, projectSlug ?? ''),
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
