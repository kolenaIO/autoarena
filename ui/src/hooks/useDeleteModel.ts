import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectUrl } from '../lib/baseRoutes.ts';
import { getModelsQueryKey } from './useModels.ts';
import { getModelEloHistoryQueryKey } from './useModelEloHistory.ts';
import { getModelHeadToHeadStatsQueryKey } from './useModelHeadToHeadStats.ts';

function getDeleteModelQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/model', 'DELETE'];
}

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, number>;
};
export function useDeleteModel({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteModelQueryKey(projectSlug),
    mutationFn: async (modelId: number) => {
      const url = `${getProjectUrl(projectSlug)}/model/${modelId}`;
      await fetch(url, { method: 'DELETE' });
    },
    onError: () => {
      notifications.show({
        title: 'Failed to delete model',
        message: 'Unable to delete model and related results',
        color: 'red',
      });
    },
    onSuccess: () => {
      notifications.show({
        title: 'Deleted model',
        message: 'Model and all related results deleted', // TODO: ideally reference the model name
        color: 'green',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectSlug) });
      queryClient.invalidateQueries({ queryKey: getModelEloHistoryQueryKey() }); // invalidate all
      queryClient.invalidateQueries({ queryKey: getModelHeadToHeadStatsQueryKey() });
    },
    ...options,
  });
}
