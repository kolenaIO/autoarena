import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from './paths.ts';

const PROJECTS_ENDPOINT = `${BASE_API_URL}/projects`;

export type Project = {
  id: number;
  name: string;
  created: string;
};

export function useProjects() {
  return useQuery({
    queryKey: [PROJECTS_ENDPOINT],
    queryFn: async () => {
      const response = await fetch(PROJECTS_ENDPOINT);
      if (!response.ok) {
        return;
      }
      const result: Project[] = await response.json();
      return result;
    },
  });
}
