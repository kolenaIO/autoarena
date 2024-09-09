import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectUrl } from '../lib/baseRoutes.ts';
import { getTasksQueryKey } from './useTasks.ts';

function getCreateFineTuningTaskQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/fine-tune'];
}

type CreateFineTuningTaskRequest = {
  base_model: string;
  // TODO: will need additional information
};

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, CreateFineTuningTaskRequest>;
};
export function useCreateFineTuningTask({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getCreateFineTuningTaskQueryKey(projectSlug),
    mutationFn: async (request: CreateFineTuningTaskRequest) => {
      const url = `${getProjectUrl(projectSlug)}/${projectSlug}`;
      const response = await fetch(url, {
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
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectSlug) });
    },
    ...options,
  });
}
