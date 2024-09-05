import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';
import { getTasksQueryKey } from './useTasks.ts';

const CLEAR_COMPLETED_TASKS_ENDPOINT = `${BASE_API_URL}/tasks`;

function getClearCompletedTasksQueryKey() {
  return [CLEAR_COMPLETED_TASKS_ENDPOINT, 'DELETE'];
}

type Params = {
  projectId?: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useClearCompletedTasks({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getClearCompletedTasksQueryKey(),
    mutationFn: async () => {
      const url = `${CLEAR_COMPLETED_TASKS_ENDPOINT}/${projectId}/completed`;
      await fetch(url, { method: 'DELETE' });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectId ?? -1) });
    },
    ...options,
  });
}
