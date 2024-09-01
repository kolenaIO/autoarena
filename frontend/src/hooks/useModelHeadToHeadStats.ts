import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

const MODEL_HEAD_TO_HEAD_STATS_ENDPOINT = `${BASE_API_URL}/model`;
const MODEL_HEAD_TO_HEAD_STATS_STUB = 'head-to-head/stats';

export function getModelHeadToHeadStatsEndpoint(modelId: number) {
  return `${MODEL_HEAD_TO_HEAD_STATS_ENDPOINT}/${modelId}/${MODEL_HEAD_TO_HEAD_STATS_STUB}`;
}

export type ModelHeadToHeadStats = {
  other_model_id: number;
  other_model_name: string;
  judge_id: number;
  judge_name: string;
  count_wins: number;
  count_losses: number;
  count_ties: number;
};

export function useModelHeadToHeadStats(modelId: number | undefined) {
  return useQuery({
    queryKey: [getModelHeadToHeadStatsEndpoint(modelId ?? -1)],
    queryFn: async () => {
      const url = getModelHeadToHeadStatsEndpoint(modelId ?? -1);
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: ModelHeadToHeadStats[] = await response.json();
      return result;
    },
    enabled: modelId != null,
  });
}
