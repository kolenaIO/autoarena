import { BASE_API_URL } from '../components/paths.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

const MODELS_ENDPOINT = `${BASE_API_URL}/models`;

export function getModelsQueryKey(projectId: number) {
  return [MODELS_ENDPOINT, projectId];
}

export type Model = {
  id: number;
  name: string;
  created: string;
  elo: number;
  q025?: number; // these are only set once models have been rated
  q975?: number;
  datapoints: number;
  votes: number;
  extra_stats: {
    [name: string]: {
      max: number;
      min: number;
      mean: number;
      median: number;
      stdev: number;
      sum: number;
    };
  };
};

export function useModels(projectId: number | undefined) {
  return useQueryWithErrorToast({
    queryKey: getModelsQueryKey(projectId ?? -1),
    queryFn: async () => {
      const url = `${MODELS_ENDPOINT}/${projectId}`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: Model[] = await response.json();
      return result;
    },
    enabled: projectId != null,
    errorMessage: 'Failed to fetch models',
  });
}
