import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { getProjectApiUrl } from '../lib/routes.ts';
import { getTasksQueryKey } from './useTasks.ts';

function getClearCompletedTasksQueryKey(projectSlug: string) {
  return [getProjectApiUrl(projectSlug), '/tasks', 'DELETE'];
}

type Params = {
  projectSlug?: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useClearCompletedTasks({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getClearCompletedTasksQueryKey(projectSlug ?? ''),
    mutationFn: async () => {
      const url = `${getProjectApiUrl(projectSlug ?? '')}/tasks/completed`;
      await fetch(url, { method: 'DELETE' });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectSlug ?? '') });
    },
    ...options,
  });
}
