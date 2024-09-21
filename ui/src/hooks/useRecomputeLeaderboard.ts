import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { API_ROUTES, urlAsQueryKey } from '../lib';
import { getModelsQueryKey } from './useModels.ts';
import { useApiFetch } from './useApiFetch.ts';

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useRecomputeLeaderboard({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useApiFetch();
  const queryClient = useQueryClient();
  const url = API_ROUTES.reseedEloScores(projectSlug);
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
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectSlug) });
    },
    ...options,
  });
}
