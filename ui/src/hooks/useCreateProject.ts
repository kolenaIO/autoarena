import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { notifications } from '@mantine/notifications';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { Project } from './useProjects.ts';
import { useAppRoutes } from './useAppRoutes.ts';

type CreateProjectRequest = {
  name: string;
};

export function useCreateProject({
  options,
}: { options?: UseMutationOptions<Project, Error, CreateProjectRequest> } = {}) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes, appRoutes } = useAppRoutes();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const url = apiRoutes.createProject();
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'PUT'),
    mutationFn: async (request: CreateProjectRequest) => {
      const response = await apiFetch(url, {
        method: 'PUT',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to create project');
      }
      const result: Project = await response.json();
      return result;
    },
    onSuccess: (project: Project) => {
      notifications.show({
        title: 'Created project',
        message: `Switched to newly created project '${project.slug}'`,
        color: 'green',
      });
      navigate(appRoutes.leaderboard(project.slug));
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getProjects()) });
    },
    ...options,
  });
}
