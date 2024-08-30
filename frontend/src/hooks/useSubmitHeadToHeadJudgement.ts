import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';
import { getModelsQueryKey } from './useModels.ts';

const SUBMIT_HEAD_TO_HEAD_JUDGEMENT_ENDPOINT = `${BASE_API_URL}/head-to-head/judgement`;

function getSubmitHeadToHeadJudgementQueryKey(projectId: number) {
  return [SUBMIT_HEAD_TO_HEAD_JUDGEMENT_ENDPOINT, projectId];
}

type HeadToHeadJudgementRequest = {
  project_id: number;
  judge_name: string;
  result_a_id: number;
  result_b_id: number;
  winner: 'A' | 'B' | '-';
};

type Params = {
  projectId: number;
  options?: UseMutationOptions<void, Error, HeadToHeadJudgementRequest>;
};
export function useSubmitHeadToHeadJudgement({ projectId, options }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getSubmitHeadToHeadJudgementQueryKey(projectId),
    mutationFn: async request => {
      const response = await fetch(SUBMIT_HEAD_TO_HEAD_JUDGEMENT_ENDPOINT, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      await response.json();
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectId) });
    },
    ...options,
  });
}
