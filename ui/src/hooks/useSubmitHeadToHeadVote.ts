import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { getProjectApiUrl } from '../lib/routes.ts';
import { getModelsQueryKey } from './useModels.ts';

function getSubmitHeadToHeadVoteQueryKey(projectSlug: string) {
  return [getProjectApiUrl(projectSlug), '/head-to-head/vote', 'POST'];
}

type HeadToHeadVoteRequest = {
  response_a_id: number;
  response_b_id: number;
  winner: 'A' | 'B' | '-';
};

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, HeadToHeadVoteRequest>;
};
export function useSubmitHeadToHeadVote({ projectSlug, options }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getSubmitHeadToHeadVoteQueryKey(projectSlug),
    mutationFn: async (request: HeadToHeadVoteRequest) => {
      const response = await fetch(`${getProjectApiUrl(projectSlug)}/head-to-head/vote`, {
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
