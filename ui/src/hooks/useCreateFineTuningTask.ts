import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { getTasksQueryKey } from './useTasks.ts';
import { useRoutes } from './useRoutes.ts';

type CreateFineTuningTaskRequest = {
  base_model: string;
  // TODO: will need additional information
};

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, CreateFineTuningTaskRequest>;
};
export function useCreateFineTuningTask({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.createFineTuningTask(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'POST'),
    mutationFn: async (request: CreateFineTuningTaskRequest) => {
      const response = await apiFetch(url, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to create fine-tuning task');
      }
    },
    onSuccess: () => {
      notifications.show({
        title: 'Fine-tuning task created',
        message: "View training progress and details in the 'tasks' drawer",
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(apiRoutes, projectSlug) });
    },
    ...options,
  });
}
