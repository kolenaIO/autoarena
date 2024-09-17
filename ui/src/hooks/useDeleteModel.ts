import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectApiUrl } from '../lib/routes.ts';
import { getModelsQueryKey } from './useModels.ts';
import { getModelHeadToHeadStatsQueryKey } from './useModelHeadToHeadStats.ts';

function getDeleteModelQueryKey(projectSlug: string) {
  return [getProjectApiUrl(projectSlug), '/model', 'DELETE'];
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
      const url = `${getProjectApiUrl(projectSlug)}/model/${modelId}`;
      await fetch(url, { method: 'DELETE' });
    },
    onError: () => {
      notifications.show({
        title: 'Failed to delete model',
        message: 'Unable to delete model and related responses',
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
      queryClient.invalidateQueries({ queryKey: getModelHeadToHeadStatsQueryKey(projectSlug) }); // invalidate all
    },
    ...options,
  });
}
