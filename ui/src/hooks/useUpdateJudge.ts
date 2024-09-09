import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { BASE_API_URL } from '../lib/baseRoutes.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';

const UPDATE_JUDGE_ENDPOINT = `${BASE_API_URL}/judge`;

function getUpdateJudgeQueryKey(projectSlug: string) {
  return [UPDATE_JUDGE_ENDPOINT, projectSlug];
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
      const response = await fetch(UPDATE_JUDGE_ENDPOINT, {
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
