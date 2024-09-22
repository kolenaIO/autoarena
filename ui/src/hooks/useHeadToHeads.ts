import { useQuery } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useRoutes } from './useRoutes.ts';

export type HeadToHeadHistoryItem = {
  judge_id: number;
  judge_name: string;
  winner: string;
};

export type HeadToHeadItem = {
  prompt: string;
  response_a_id: number;
  response_a: string;
  response_b_id: number;
  response_b: string;
  history: HeadToHeadHistoryItem[];
};

type Params = {
  projectSlug: string;
  modelAId: number;
  modelBId: number;
};
export function useHeadToHeads({ projectSlug, modelAId, modelBId }: Params) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useRoutes();
  const url = apiRoutes.getHeadToHeads(projectSlug);
  return useQuery({
    queryKey: [...urlAsQueryKey(url), modelAId, modelBId],
    queryFn: async () => {
      const body = { model_a_id: modelAId, model_b_id: modelBId };
      const response = await apiFetch(url, {
        method: 'PUT',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch head-to-heads');
      }
      const result: HeadToHeadItem[] = await response.json();
      return result;
    },
  });
}
