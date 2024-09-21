import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { getJudgesQueryKey, Judge } from './useJudges.ts';
import { useRoutes } from './useRoutes.ts';

type UpdateJudgeRequest = {
  enabled: boolean;
};

type Params = {
  projectSlug: string;
  judgeId: number;
  options?: UseMutationOptions<Judge, Error, UpdateJudgeRequest>;
};
export function useUpdateJudge({ projectSlug, judgeId, options = {} }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.updateJudge(projectSlug, judgeId);
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
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(apiRoutes, projectSlug) });
    },
    ...options,
  });
}
