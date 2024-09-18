import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { getProjectsQueryKey } from './useProjects.ts';

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, void>;
};
export function useDeleteProject({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  const url = API_ROUTES.deleteProject(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'DELETE'),
    mutationFn: async () => {
      const response = await fetch(url, { method: 'DELETE' });
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
      queryClient.invalidateQueries({ queryKey: getProjectsQueryKey() });
    },
    ...options,
  });
}
