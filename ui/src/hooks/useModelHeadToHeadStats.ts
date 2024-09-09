import { useQuery } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';

export function getModelHeadToHeadStatsEndpoint(projectSlug: string, modelId: number) {
  return `${getProjectUrl(projectSlug)}/model/${modelId}/head-to-head/stats`;
}

export function getModelHeadToHeadStatsQueryKey(projectSlug: string, modelId?: number) {
  return [getProjectUrl(projectSlug), '/model', modelId, '/head-to-head/stats'];
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
  return useQuery({
    queryKey: getModelHeadToHeadStatsQueryKey(projectSlug ?? '', modelId),
    queryFn: async () => {
      const url = getModelHeadToHeadStatsEndpoint(projectSlug ?? '', modelId ?? -1);
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: ModelHeadToHeadStats[] = await response.json();
      return result;
    },
    enabled: projectSlug != null && modelId != null,
  });
}
