import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { getTasksQueryKey } from './useTasks.ts';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug?: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useClearCompletedTasks({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.deleteCompletedTasks(projectSlug ?? '');
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'DELETE'),
    mutationFn: async () => {
      const response = await apiFetch(url, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to clear completed tasks');
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(apiRoutes, projectSlug ?? '') });
    },
    ...options,
  });
}
