import { useQuery } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';

function getModelEloHistoryEndpoint(projectSlug: string, modelId: number, judgeId: number | undefined) {
  const params = judgeId != null ? new URLSearchParams({ judge_id: String(judgeId) }) : undefined;
  const url = `${getProjectUrl(projectSlug)}/model/${modelId}/elo-history`;
  return params != null ? `${url}?${params}` : url;
}

export function getModelEloHistoryQueryKey(projectSlug: string, modelId?: number, judgeId?: number) {
  return [getProjectUrl(projectSlug), '/model', modelId, '/elo-history', judgeId];
}

export type EloHistoryItem = {
  other_model_id: number;
  other_model_name: string;
  judge_id: number;
  judge_name: string;
  elo: number;
};

type Params = {
  projectSlug?: string;
  modelId?: number;
  judgeId?: number;
};
export function useModelEloHistory({ projectSlug, modelId, judgeId }: Params) {
  return useQuery({
    queryKey: getModelEloHistoryQueryKey(projectSlug ?? '', modelId, judgeId),
    queryFn: async () => {
      const url = getModelEloHistoryEndpoint(projectSlug ?? '', modelId ?? -1, judgeId);
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: EloHistoryItem[] = await response.json();
      return result;
    },
    enabled: projectSlug != null && modelId != null,
  });
}
