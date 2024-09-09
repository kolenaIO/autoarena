import { useQuery } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/baseRoutes.ts';

export type HeadToHeadHistoryItem = {
  judge_id: number;
  judge_name: string;
  winner: string;
};

export type HeadToHead = {
  prompt: string;
  result_a_id: number;
  response_a: string;
  result_b_id: number;
  response_b: string;
  history: HeadToHeadHistoryItem[];
};

type Params = {
  projectSlug: string;
  modelAId: number;
  modelBId: number;
};
export function useHeadToHeads({ projectSlug, modelAId, modelBId }: Params) {
  return useQuery({
    queryKey: [getProjectUrl(projectSlug), '/head-to-heads', modelAId, modelBId],
    queryFn: async () => {
      const body = { model_a_id: modelAId, model_b_id: modelBId };
      const response = await fetch(`${getProjectUrl(projectSlug)}/head-to-heads`, {
        method: 'PUT',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        return;
      }
      const result: HeadToHead[] = await response.json();
      return result;
    },
  });
}
