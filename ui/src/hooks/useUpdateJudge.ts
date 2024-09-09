import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';

function getUpdateJudgeQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/judge'];
}

type UpdateJudgeRequest = {
  judge_id: number;
  enabled: boolean;
};

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<Judge, Error, UpdateJudgeRequest>;
};
export function useUpdateJudge({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getUpdateJudgeQueryKey(projectSlug),
    mutationFn: async (request: UpdateJudgeRequest) => {
      const response = await fetch(`${getProjectUrl(projectSlug)}/judge`, {
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
