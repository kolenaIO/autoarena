import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from './paths.ts';

const MODELS_ENDPOINT = `${BASE_API_URL}/models`;

export type Model = {
  id: number;
  name: string;
  created: string;
  elo: number;
  q025: number;
  q975: number;
  votes: number;
};

export function useModels(projectId: number) {
  return useQuery({
    queryKey: [MODELS_ENDPOINT, projectId],
    queryFn: async () => {
      const url = `${MODELS_ENDPOINT}/${projectId}`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: Model[] = await response.json();
      return result;
    },
  });
}
