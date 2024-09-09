import { getProjectUrl } from '../lib/routes.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

export function getModelsQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/models'];
}

export type Model = {
  id: number;
  name: string;
  created: string;
  elo: number;
  q025?: number; // these are only set once models have been rated
  q975?: number;
  n_responses: number;
  votes: number;
};

export function useModels(projectSlug: string | undefined) {
  return useQueryWithErrorToast({
    queryKey: getModelsQueryKey(projectSlug ?? ''),
    queryFn: async () => {
      const response = await fetch(`${getProjectUrl(projectSlug ?? '')}/models`);
      if (!response.ok) {
        return;
      }
      const result: Model[] = await response.json();
      return result;
    },
    enabled: projectSlug != null,
    errorMessage: 'Failed to fetch models',
  });
}
