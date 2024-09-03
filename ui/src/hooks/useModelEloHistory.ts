import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

function getModelEloHistoryEndpoint(modelId: number) {
  return `${BASE_API_URL}/model/${modelId}/elo-history`;
}

export function getModelEloHistoryQueryKey(modelId?: number) {
  return ['model', 'elo-history', ...(modelId != null ? [modelId] : [])];
}

export type EloHistoryItem = {
  other_model_id: number;
  other_model_name: string;
  judge_id: number;
  judge_name: string;
  elo: number;
};

export function useModelEloHistory(modelId: number | undefined) {
  return useQuery({
    queryKey: getModelEloHistoryQueryKey(modelId),
    queryFn: async () => {
      const url = getModelEloHistoryEndpoint(modelId ?? -1);
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: EloHistoryItem[] = await response.json();
      return result;
    },
    enabled: modelId != null,
  });
}
