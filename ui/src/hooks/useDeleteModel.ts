import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { getModelsQueryKey } from './useModels.ts';
import { getModelHeadToHeadStatsQueryKey } from './useModelHeadToHeadStats.ts';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  modelId: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useDeleteModel({ projectSlug, modelId, options = {} }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.deleteModel(projectSlug, modelId);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'DELETE'),
    mutationFn: async () => {
      const response = await apiFetch(url, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete model');
      }
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
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(apiRoutes, projectSlug) });
      queryClient.invalidateQueries({ queryKey: getModelHeadToHeadStatsQueryKey(apiRoutes, projectSlug) }); // invalidate all
    },
    ...options,
  });
}
