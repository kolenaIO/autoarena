import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../components/paths.ts';
import { getModelsQueryKey } from './useModels.ts';
import { getModelEloHistoryQueryKey } from './useModelEloHistory.ts';
import { getModelHeadToHeadStatsQueryKey } from './useModelHeadToHeadStats.ts';

const DELETE_MODEL_ENDPOINT = `${BASE_API_URL}/model`;

function getDeleteModelQueryKey() {
  return [DELETE_MODEL_ENDPOINT];
}

type Params = {
  projectId: number;
  options?: UseMutationOptions<void, Error, number>;
};
export function useDeleteModel({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteModelQueryKey(),
    mutationFn: async (modelId: number) => {
      const url = `${DELETE_MODEL_ENDPOINT}/${modelId}`;
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
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectId) });
      queryClient.invalidateQueries({ queryKey: getModelEloHistoryQueryKey() }); // invalidate all
      queryClient.invalidateQueries({ queryKey: getModelHeadToHeadStatsQueryKey() });
    },
    ...options,
  });
}
