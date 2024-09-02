import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../components/paths.ts';
import { getTasksQueryKey } from './useTasks.ts';

const CREATE_FINE_TUNING_TASK_ENDPOINT = `${BASE_API_URL}/fine-tune`;

function getCreateFineTuningTaskQueryKey(projectId: number) {
  return [CREATE_FINE_TUNING_TASK_ENDPOINT, projectId];
}

type CreateFineTuningTaskRequest = {
  base_model: string;
  // TODO: will need additional information
};

type Params = {
  projectId: number;
  options?: UseMutationOptions<void, Error, CreateFineTuningTaskRequest>;
};
export function useCreateFineTuningTask({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getCreateFineTuningTaskQueryKey(projectId),
    mutationFn: async (request: CreateFineTuningTaskRequest) => {
      const url = `${CREATE_FINE_TUNING_TASK_ENDPOINT}/${projectId}`;
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
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectId) });
    },
    ...options,
  });
}
