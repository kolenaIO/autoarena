import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../components/paths.ts';
import { PROJECTS_QUERY_KEY } from './useProjects.ts';

const DELETE_PROJECT_ENDPOINT = `${BASE_API_URL}/project`;

function getDeleteProjectQueryKey() {
  return [DELETE_PROJECT_ENDPOINT, 'DELETE'];
}

type Params = {
  options?: UseMutationOptions<void, Error, number>;
};
export function useDeleteProject({ options }: Params = {}) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getDeleteProjectQueryKey(),
    mutationFn: async (projectId: number) => {
      const url = `${DELETE_PROJECT_ENDPOINT}/${projectId}`;
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
