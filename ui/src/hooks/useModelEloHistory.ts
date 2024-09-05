import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

function getModelEloHistoryEndpoint(modelId: number, judgeId: number | undefined) {
  const params = judgeId != null ? new URLSearchParams({ judge_id: String(judgeId) }) : undefined;
  const url = `${BASE_API_URL}/model/${modelId}/elo-history`;
  return params != null ? `${url}?${params}` : url;
}

export function getModelEloHistoryQueryKey(modelId: number | undefined, judgeId: number | undefined) {
  return ['model', 'elo-history', ...(modelId != null ? [modelId] : []), ...(judgeId != null ? [judgeId] : [])];
}

export type EloHistoryItem = {
  other_model_id: number;
  other_model_name: string;
  judge_id: number;
  judge_name: string;
  elo: number;
};

export function useModelEloHistory(modelId: number | undefined, judgeId: number | undefined) {
  return useQuery({
    queryKey: getModelEloHistoryQueryKey(modelId, judgeId),
    queryFn: async () => {
      const url = getModelEloHistoryEndpoint(modelId ?? -1, judgeId);
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
