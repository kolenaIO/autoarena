import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

const JUDGES_ENDPOINT = `${BASE_API_URL}/judges`;

export function getJudgesQueryKey(projectId: number) {
  return [JUDGES_ENDPOINT, projectId];
}

export type Judge = {
  id: number;
  judge_type: 'human' | 'ollama' | 'openai' | 'gemini' | 'anthropic' | 'cohere' | 'custom';
  created: string;
  name: string;
  description: string;
  enabled: boolean;
};

export function useJudges(projectId: number | undefined) {
  return useQuery({
    queryKey: getJudgesQueryKey(projectId ?? -1),
    queryFn: async () => {
      const url = `${JUDGES_ENDPOINT}/${projectId}`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: Judge[] = await response.json();
      return result;
    },
    enabled: projectId != null,
  });
}
