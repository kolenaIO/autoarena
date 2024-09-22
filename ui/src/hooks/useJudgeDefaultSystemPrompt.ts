import { useQuery } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useAppRoutes } from './useAppRoutes.ts';

export function useJudgeDefaultSystemPrompt(projectSlug: string) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.getDefaultSystemPrompt(projectSlug);
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
