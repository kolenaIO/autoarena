import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectApiUrl } from '../lib/routes.ts';
import { getJudgesQueryKey } from './useJudges.ts';
import { getModelHeadToHeadStatsQueryKey } from './useModelHeadToHeadStats.ts';

function getDeleteJudgeQueryKey(projectSlug: string) {
  return [getProjectApiUrl(projectSlug), '/judge', 'DELETE'];
}

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, number>;
};
export function useDeleteJudge({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteJudgeQueryKey(projectSlug),
    mutationFn: async (judgeId: number) => {
      const url = `${getProjectApiUrl(projectSlug)}/judge/${judgeId}`;
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
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectSlug) });
      queryClient.invalidateQueries({ queryKey: getModelHeadToHeadStatsQueryKey(projectSlug) }); // invalidate all
    },
    ...options,
  });
}
