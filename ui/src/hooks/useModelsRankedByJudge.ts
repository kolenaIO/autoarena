import { urlAsQueryKey, useAppConfig } from '../lib';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { Model } from './useModels.ts';
import { useAppRoutes } from './useAppRoutes.ts';

export function useModelsRankedByJudge(projectSlug: string | undefined, judgeId: number | undefined) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.getModelsRankedByJudge(projectSlug ?? '', judgeId ?? -1);
  return useQueryWithErrorToast({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch models ranked by judge');
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
