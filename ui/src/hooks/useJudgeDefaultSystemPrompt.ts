import { useQuery } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib';
import { useApiFetch } from './useApiFetch.ts';

export function useJudgeDefaultSystemPrompt(projectSlug: string) {
  const { apiFetch } = useApiFetch();
  const url = API_ROUTES.getDefaultSystemPrompt(projectSlug);
  return useQuery({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch default judge system prompt');
      }
      const result: string = await response.json();
      return result;
    },
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchInterval: Infinity,
  });
}
