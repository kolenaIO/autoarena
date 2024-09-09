import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL, getProjectUrl } from '../lib/routes.ts';
import { PROJECTS_QUERY_KEY } from './useProjects.ts';

function getDeleteProjectQueryKey() {
  return [`${BASE_API_URL}/project`, 'DELETE'];
}

type Params = {
  options?: UseMutationOptions<void, Error, string>;
};
export function useDeleteProject({ options }: Params = {}) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteProjectQueryKey(),
    mutationFn: async (projectSlug: string) => {
      const url = getProjectUrl(projectSlug);
      await fetch(url, { method: 'DELETE' });
    },
    onError: () => {
      notifications.show({
        title: 'Failed to delete project',
        message: 'Unable to delete project and related models, judges, and head-to-heads',
        color: 'red',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY });
    },
    ...options,
  });
}
