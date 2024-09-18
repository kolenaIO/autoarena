import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';
import { useApiFetch } from './useApiFetch.ts';

type UpdateJudgeRequest = {
  enabled: boolean;
};

type Params = {
  projectSlug: string;
  judgeId: number;
  options?: UseMutationOptions<Judge, Error, UpdateJudgeRequest>;
};
export function useUpdateJudge({ projectSlug, judgeId, options = {} }: Params) {
  const { apiFetch } = useApiFetch();
  const queryClient = useQueryClient();
  const url = API_ROUTES.updateJudge(projectSlug, judgeId);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'PUT'),
    mutationFn: async (request: UpdateJudgeRequest) => {
      const response = await apiFetch(url, {
        method: 'PUT',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to update judge');
      }
      const result: Judge = await response.json();
      return result;
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectSlug) });
    },
    ...options,
  });
}
