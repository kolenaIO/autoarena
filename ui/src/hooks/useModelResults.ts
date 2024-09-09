import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../lib/baseRoutes.ts';

function getModelResultsEndpoint(modelId: number) {
  return `${BASE_API_URL}/model/${modelId}/results`;
}

export function getModelResultsQueryKey(modelId: number) {
  return [`${BASE_API_URL}/model`, modelId, '/results'];
}

export type ModelResult = {
  prompt: string;
  response: string;
};

export function useModelResults(modelId: number | undefined) {
  return useQuery({
    queryKey: getModelResultsQueryKey(modelId ?? -1),
    queryFn: async () => {
      const url = getModelResultsEndpoint(modelId ?? -1);
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: ModelResult[] = await response.json();
      return result;
    },
    enabled: modelId != null,
  });
}
