import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useAppRoutes } from './useAppRoutes.ts';

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
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.submitHeadToHeadVote(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'POST'),
    mutationFn: async (request: HeadToHeadVoteRequest) => {
      const response = await apiFetch(url, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to submit vote');
      }
      await response.json();
      await new Promise(resolve => setTimeout(resolve, 500)); // add some delay to debounce
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getModels(projectSlug)) });
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getHeadToHeads(projectSlug)) });
    },
    ...options,
  });
}
