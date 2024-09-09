import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';
import { getModelsQueryKey } from './useModels.ts';

function getSubmitHeadToHeadJudgementQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/head-to-head/judgement', 'POST'];
}

type HeadToHeadJudgementRequest = {
  result_a_id: number;
  result_b_id: number;
  winner: 'A' | 'B' | '-';
};

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, HeadToHeadJudgementRequest>;
};
export function useSubmitHeadToHeadJudgement({ projectSlug, options }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getSubmitHeadToHeadJudgementQueryKey(projectSlug),
    mutationFn: async (request: HeadToHeadJudgementRequest) => {
      const response = await fetch(`${getProjectUrl(projectSlug)}/head-to-head/judgement`, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      await response.json();
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectSlug) });
    },
    ...options,
  });
}
