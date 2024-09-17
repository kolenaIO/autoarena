import { useQuery } from '@tanstack/react-query';
import { getProjectApiUrl } from '../lib/routes.ts';

export type HeadToHeadHistoryItem = {
  judge_id: number;
  judge_name: string;
  winner: string;
};

export type HeadToHead = {
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
  return useQuery({
    queryKey: [getProjectApiUrl(projectSlug), '/head-to-heads', modelAId, modelBId],
    queryFn: async () => {
      const body = { model_a_id: modelAId, model_b_id: modelBId };
      const response = await fetch(`${getProjectApiUrl(projectSlug)}/head-to-heads`, {
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
