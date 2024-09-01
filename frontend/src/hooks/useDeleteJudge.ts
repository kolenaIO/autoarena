import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../components/paths.ts';
import { getJudgesQueryKey } from './useJudges.ts';

const DELETE_JUDGE_ENDPOINT = `${BASE_API_URL}/judge`;

function getDeleteJudgeQueryKey() {
  return [DELETE_JUDGE_ENDPOINT];
}

type Params = {
  projectId: number;
  options?: UseMutationOptions<void, Error, number>;
};
export function useDeleteJudge({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteJudgeQueryKey(),
    mutationFn: async (judgeId: number) => {
      const url = `${DELETE_JUDGE_ENDPOINT}/${judgeId}`;
      await fetch(url, { method: 'DELETE' });
    },
    onError: () => {
      notifications.show({
        title: 'Failed to delete judge',
        message: 'Unable to delete judge and related votes',
        color: 'red',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectId) });
    },
    ...options,
  });
}
