import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { API_ROUTES, getBaseApiUrl } from '../lib/routes.ts';
import { getProjectsQueryKey } from './useProjects.ts';

function getDeleteProjectQueryKey() {
  return [`${getBaseApiUrl()}/project`, 'DELETE'];
}

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, string>;
};
export function useDeleteProject({ projectSlug, options = {} }: Params) {
  const queryClient = useQueryClient();
  const url = API_ROUTES.deleteProject(projectSlug);
  return useMutation({
    mutationKey: getDeleteProjectQueryKey(),
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
