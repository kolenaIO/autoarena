import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useRecomputeLeaderboard({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.reseedEloScores(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'PUT'),
    mutationFn: async () => {
      const response = await apiFetch(url, { method: 'PUT' });
      if (!response.ok) {
        throw new Error('Failed to recompute leaderboard rankings');
      }
    },
    onSuccess: () => {
      notifications.show({
        title: 'Recomputed leaderboard Rankings',
        message: 'Recalculated Elo scores and confidence intervals',
        color: 'green',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getModels(projectSlug)) });
    },
    ...options,
  });
}
