import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { BASE_API_URL } from '../components/paths.ts';
import { Project, PROJECTS_QUERY_KEY } from './useProjects.ts';

const CREATE_PROJECT_ENDPOINT = `${BASE_API_URL}/project`;

type CreateProjectRequest = {
  name: string;
};

export function useCreateProject({
  options,
}: { options?: UseMutationOptions<Project, Error, CreateProjectRequest> } = {}) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: [CREATE_PROJECT_ENDPOINT],
    mutationFn: async (data: CreateProjectRequest) => {
      const response = await fetch(CREATE_PROJECT_ENDPOINT, {
        method: 'PUT',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' },
      });
      const result: Project = await response.json();
      return result;
    },
    onSettled: project => {
      queryClient.invalidateQueries({ queryKey: PROJECTS_QUERY_KEY });
      navigate(`/project/${project?.id}`);
    },
    ...options,
  });
}
