import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

const HEAD_TO_HEADS_ENDPOINT = `${BASE_API_URL}/head-to-heads`;

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
  modelAId: number;
  modelBId: number;
};
export function useHeadToHeads({ modelAId, modelBId }: Params) {
  return useQuery({
    queryKey: [HEAD_TO_HEADS_ENDPOINT, modelAId, modelBId],
    queryFn: async () => {
      const body = { model_a_id: modelAId, model_b_id: modelBId };
      const response = await fetch(HEAD_TO_HEADS_ENDPOINT, {
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
