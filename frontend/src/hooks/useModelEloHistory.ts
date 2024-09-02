import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

function getModelEloHistoryEndpoint(modelId: number) {
  return `${BASE_API_URL}/model/${modelId}/elo-history`;
}

export function getModelEloHistoryQueryKey(modelId: number) {
  return [`${BASE_API_URL}/model`, modelId, '/elo-history'];
}

export function useModelEloHistory(modelId: number | undefined) {
  return useQuery({
    queryKey: getModelEloHistoryQueryKey(modelId ?? -1),
    queryFn: async () => {
      const url = getModelEloHistoryEndpoint(modelId ?? -1);
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: number[] = await response.json();
      return result;
    },
    enabled: modelId != null,
  });
}
