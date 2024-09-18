import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import {API_ROUTES, getProjectApiUrl, urlAsQueryKey} from '../lib/routes.ts';
import { getJudgesQueryKey } from './useJudges.ts';
import { getModelHeadToHeadStatsQueryKey } from './useModelHeadToHeadStats.ts';

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, number>;
};
export function useDeleteJudge({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  const url = API_ROUTES.deleteJudge(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'DELETE'),
    mutationFn: async (judgeId: number) => {
      const response= await fetch(url, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete judge')
      }
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
