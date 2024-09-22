import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  judgeId: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useDeleteJudge({ projectSlug, judgeId, options = {} }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.deleteJudge(projectSlug, judgeId);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'DELETE'),
    mutationFn: async () => {
      const response = await apiFetch(url, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete judge');
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
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getJudges(projectSlug)) });
      const h2hStatsKey = urlAsQueryKey(apiRoutes.getHeadToHeadStats(projectSlug, -1), undefined);
      queryClient.invalidateQueries({ queryKey: h2hStatsKey.slice(0, h2hStatsKey.length - 1) }); // invalidate all
    },
    ...options,
  });
}
