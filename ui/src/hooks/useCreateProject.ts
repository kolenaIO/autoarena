import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { notifications } from '@mantine/notifications';
import { useContext } from 'react';
import { API_ROUTES, AppConfigContext, ROUTES, urlAsQueryKey } from '../lib';
import { getProjectsQueryKey, Project } from './useProjects.ts';
import { useRoutes } from './useRoutes.ts';

type CreateProjectRequest = {
  name: string;
};

export function useCreateProject({
  options,
}: { options?: UseMutationOptions<Project, Error, CreateProjectRequest> } = {}) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const url = API_ROUTES.createProject();
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
      navigate(ROUTES.leaderboard(project.slug));
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getProjectsQueryKey() });
    },
    ...options,
  });
}
