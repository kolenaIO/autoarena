import { getBaseApiUrl } from '../lib/routes.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

const PROJECTS_ENDPOINT = `${getBaseApiUrl()}/projects`;
export const PROJECTS_QUERY_KEY = [PROJECTS_ENDPOINT];

export type Project = {
  slug: string;
  filename: string;
  filepath: string;
};

export function useProjects() {
  return useQueryWithErrorToast({
    queryKey: PROJECTS_QUERY_KEY,
    queryFn: async () => {
      const response = await fetch(PROJECTS_ENDPOINT);
      if (!response.ok) {
        return;
      }
      const result: Project[] = await response.json();
      return result;
    },
    errorMessage: 'Failed to fetch projects',
  });
}
