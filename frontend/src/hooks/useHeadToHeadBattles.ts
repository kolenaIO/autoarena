import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

const BATTLES_ENDPOINT = `${BASE_API_URL}/battles`;

export type Battle = {
  id: number;
  prompt: string;
  response_a: string;
  response_b: string;
};

type Params = {
  projectId: number;
  modelAId: number;
  modelBId: number;
};
export function useHeadToHeadBattles({ projectId, modelAId, modelBId }: Params) {
  return useQuery({
    queryKey: [BATTLES_ENDPOINT, modelAId, modelBId],
    queryFn: async () => {
      const body = { project_id: projectId, model_a_id: modelAId, model_b_id: modelBId };
      const response = await fetch(BATTLES_ENDPOINT, {
        method: 'PUT',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        return;
      }
      const result: Battle[] = await response.json();
      return result;
    },
  });
}
