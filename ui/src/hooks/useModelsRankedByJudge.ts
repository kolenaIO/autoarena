import { BASE_API_URL } from '../components/paths.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { Model } from './useModels.ts';

const MODELS_RANKED_BY_JUDGE_ENDPOINT = `${BASE_API_URL}/models`;

export function getJudgesRankedByModel(projectId: number | undefined, judgeId: number | undefined) {
  return [MODELS_RANKED_BY_JUDGE_ENDPOINT, projectId, 'by-judge', judgeId];
}

export function useModelsRankedByJudge(projectId: number | undefined, judgeId: number | undefined) {
  return useQueryWithErrorToast({
    queryKey: getJudgesRankedByModel(projectId, judgeId),
    queryFn: async () => {
      const response = await fetch(`${MODELS_RANKED_BY_JUDGE_ENDPOINT}/${projectId}/by-judge/${judgeId}`);
      if (!response.ok) {
        return;
      }
      const result: Model[] = await response.json();
      return result;
    },
    enabled: projectId != null && judgeId != null,
    errorMessage: 'Failed to fetch models ranked by judge',
    refetchInterval: Infinity, // do not refetch as confidence intervals may jitter a bit
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchOnWindowFocus: false,
    staleTime: Infinity,
  });
}
