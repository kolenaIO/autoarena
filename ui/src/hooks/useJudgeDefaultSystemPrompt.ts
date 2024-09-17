import { useQuery } from '@tanstack/react-query';
import { getProjectApiUrl } from '../lib/routes.ts';

function getJudgeDefaultSystemPromptQueryKey(projectSlug: string) {
  return [getProjectApiUrl(projectSlug), '/judge/default-system-prompt'];
}

export function useJudgeDefaultSystemPrompt(projectSlug: string) {
  return useQuery({
    queryKey: getJudgeDefaultSystemPromptQueryKey(projectSlug),
    queryFn: async () => {
      const response = await fetch(`${getProjectApiUrl(projectSlug)}/judge/default-system-prompt`);
      if (!response.ok) {
        return;
      }
      const result: string = await response.json();
      return result;
    },
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchInterval: Infinity,
  });
}
