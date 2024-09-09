import { getProjectUrl } from '../lib/baseRoutes.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { Model } from './useModels.ts';

export function getJudgesRankedByModel(projectSlug: string | undefined, judgeId: number | undefined) {
  return [getProjectUrl(projectSlug ?? ''), '/models', '/by-judge', judgeId];
}

export function useModelsRankedByJudge(projectSlug: string | undefined, judgeId: number | undefined) {
  return useQueryWithErrorToast({
    queryKey: getJudgesRankedByModel(projectSlug, judgeId),
    queryFn: async () => {
      const response = await fetch(`${getProjectUrl(projectSlug ?? '')}/models/by-judge/${judgeId}`);
      if (!response.ok) {
        return;
      }
      const result: Model[] = await response.json();
      return result;
    },
    enabled: projectSlug != null && judgeId != null,
    errorMessage: 'Failed to fetch models ranked by judge',
    refetchInterval: Infinity, // do not refetch as confidence intervals may jitter a bit
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchOnWindowFocus: false,
    staleTime: Infinity,
  });
}
