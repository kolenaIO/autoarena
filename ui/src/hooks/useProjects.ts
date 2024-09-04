import { BASE_API_URL } from '../components/paths.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

const PROJECTS_ENDPOINT = `${BASE_API_URL}/projects`;
export const PROJECTS_QUERY_KEY = [PROJECTS_ENDPOINT];

export type Project = {
  id: number;
  name: string;
  created: string;
};

export function useProjects() {
  return useQueryWithErrorToast({
    queryKey: [PROJECTS_ENDPOINT],
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
