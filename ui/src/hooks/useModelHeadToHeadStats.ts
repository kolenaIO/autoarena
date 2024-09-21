import { useQuery } from '@tanstack/react-query';
import { useContext } from 'react';
import { API_ROUTES, AppConfigContext, urlAsQueryKey } from '../lib';
import { useRoutes } from './useRoutes.ts';

export function getModelHeadToHeadStatsQueryKey(projectSlug: string, modelId?: number) {
  return urlAsQueryKey(API_ROUTES.getHeadToHeadStats(projectSlug, modelId ?? -1));
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

type Params = {
  projectSlug?: string;
  modelId?: number;
};
export function useModelHeadToHeadStats({ projectSlug, modelId }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const url = apiRoutes.getHeadToHeadStats(projectSlug ?? '', modelId ?? -1);
  return useQuery({
    queryKey: getModelHeadToHeadStatsQueryKey(projectSlug ?? '', modelId),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch head-to-head stats');
      }
      const result: ModelHeadToHeadStats[] = await response.json();
      return result;
    },
    enabled: projectSlug != null && modelId != null,
  });
}
