import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { useApiFetch } from './useApiFetch.ts';

export function getProjectsQueryKey() {
  return urlAsQueryKey(API_ROUTES.getProjects());
}

export type Project = {
  slug: string;
  filename: string;
  filepath: string;
};

export function useProjects() {
  const { apiFetch } = useApiFetch();
  return useQueryWithErrorToast({
    queryKey: getProjectsQueryKey(),
    queryFn: async () => {
      const response = await apiFetch(API_ROUTES.getProjects());
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      const result: Project[] = await response.json();
      return result;
    },
    errorMessage: 'Failed to fetch projects',
  });
}
