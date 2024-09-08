import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../components/paths.ts';
import { getModelsQueryKey } from './useModels.ts';

const RECOMPUTE_LEADERBOARD_ENDPOINT = `${BASE_API_URL}/elo/reseed-scores`;

function getDeleteJudgeQueryKey() {
  return [RECOMPUTE_LEADERBOARD_ENDPOINT];
}

type Params = {
  projectId: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useRecomputeLeaderboard({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteJudgeQueryKey(),
    mutationFn: async () => {
      const url = `${RECOMPUTE_LEADERBOARD_ENDPOINT}/${projectId}`;
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
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectId) });
    },
    ...options,
  });
}
