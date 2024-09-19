import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { getTasksQueryKey } from './useTasks.ts';
import { useApiFetch } from './useApiFetch.ts';

type Params = {
  projectSlug?: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useClearCompletedTasks({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useApiFetch();
  const queryClient = useQueryClient();
  const url = API_ROUTES.deleteCompletedTasks(projectSlug ?? '');
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'DELETE'),
    mutationFn: async () => {
      const response = await apiFetch(url, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to clear completed tasks');
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectSlug ?? '') });
    },
    ...options,
  });
}
