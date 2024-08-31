import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';

const DELETE_JUDGE_ENDPOINT = `${BASE_API_URL}/judge`;

function getDeleteJudgeQueryKey() {
  return [DELETE_JUDGE_ENDPOINT];
}

type Params = {
  projectId: number;
  options?: UseMutationOptions<Judge, Error, number>;
};
export function useDeleteJudge({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteJudgeQueryKey(),
    mutationFn: async (judgeId: number) => {
      const url = `${DELETE_JUDGE_ENDPOINT}/${judgeId}`;
      await fetch(url, { method: 'DELETE' });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectId) });
    },
    ...options,
  });
}
