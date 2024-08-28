import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from './paths.ts';

const MODELS_ENDPOINT = `${BASE_API_URL}/models`;

export type Model = {
  id: number;
  name: string;
};

export function useModels() {
  return useQuery({
    queryKey: [MODELS_ENDPOINT],
    queryFn: async () => {
      const response = await fetch(MODELS_ENDPOINT);
      if (!response.ok) {
        return;
      }
      const result: Model[] = await response.json();
      return result;
    },
  });
}
