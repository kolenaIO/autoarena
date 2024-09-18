import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { getModelsQueryKey } from './useModels.ts';

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
  const url = API_ROUTES.submitHeadToHeadVote(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'POST'),
    mutationFn: async (request: HeadToHeadVoteRequest) => {
      const response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to submit vote');
      }
      await response.json();
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectSlug) });
    },
    ...options,
  });
}
