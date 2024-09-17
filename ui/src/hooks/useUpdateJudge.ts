import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { getProjectApiUrl } from '../lib/routes.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';

function getUpdateJudgeQueryKey(projectSlug: string, judgeId: number) {
  return [getProjectApiUrl(projectSlug), '/judge', judgeId];
}

type UpdateJudgeRequest = {
  enabled: boolean;
};

type Params = {
  projectSlug: string;
  judgeId: number;
  options?: UseMutationOptions<Judge, Error, UpdateJudgeRequest>;
};
export function useUpdateJudge({ projectSlug, judgeId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getUpdateJudgeQueryKey(projectSlug, judgeId),
    mutationFn: async (request: UpdateJudgeRequest) => {
      const response = await fetch(`${getProjectApiUrl(projectSlug)}/judge/${judgeId}`, {
        method: 'PUT',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      const result: Judge = await response.json();
      return result;
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectSlug) });
    },
    ...options,
  });
}
