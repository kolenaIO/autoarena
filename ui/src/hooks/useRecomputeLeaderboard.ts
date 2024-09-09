import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectUrl } from '../lib/routes.ts';
import { getModelsQueryKey } from './useModels.ts';

function getDeleteJudgeQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/elo/reseed-scores'];
}

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useRecomputeLeaderboard({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteJudgeQueryKey(projectSlug),
    mutationFn: async () => {
      const url = `${getProjectUrl(projectSlug)}/elo/reseed-scores`;
      await fetch(url, { method: 'PUT' });
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
