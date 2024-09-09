import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../lib/routes.ts';
import { Project, PROJECTS_QUERY_KEY } from './useProjects.ts';

type CreateProjectRequest = {
  name: string;
};

export function useCreateProject({
  options,
}: { options?: UseMutationOptions<Project, Error, CreateProjectRequest> } = {}) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: [`${BASE_API_URL}/project`],
    mutationFn: async (request: CreateProjectRequest) => {
      const response = await fetch(`${BASE_API_URL}/project`, {
        method: 'PUT',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      const result: Project = await response.json();
      return result;
    },
    onSuccess: (project: Project) => {
      notifications.show({
        title: 'Created project',
        message: `Switched to newly created project '${project.slug}'`,
        color: 'green',
      });
      navigate(`/project/${project.slug}`);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY });
    },
    ...options,
  });
}
