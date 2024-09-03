import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';

const UPDATE_JUDGE_ENDPOINT = `${BASE_API_URL}/judge`;

function getUpdateJudgeQueryKey(projectId: number) {
  return [UPDATE_JUDGE_ENDPOINT, projectId];
}

type UpdateJudgeRequest = {
  project_id: number;
  judge_id: number;
  enabled: boolean;
};

type Params = {
  projectId: number;
  options?: UseMutationOptions<Judge, Error, UpdateJudgeRequest>;
};
export function useUpdateJudge({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getUpdateJudgeQueryKey(projectId),
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
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectId) });
    },
    ...options,
  });
}
