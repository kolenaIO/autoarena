import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useDeleteProject({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.deleteProject(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'DELETE'),
    mutationFn: async () => {
      const response = await apiFetch(url, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete project');
      }
    },
    onError: () => {
      notifications.show({
        title: 'Failed to delete project',
        message: 'Unable to delete project and related models, judges, and head-to-heads',
        color: 'red',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getProjects()) });
    },
    ...options,
  });
}
