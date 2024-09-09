import { useQuery } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';

function getJudgeDefaultSystemPromptQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/judge/default-system-prompt'];
}

export function useJudgeDefaultSystemPrompt(projectSlug: string) {
  return useQuery({
    queryKey: getJudgeDefaultSystemPromptQueryKey(projectSlug),
    queryFn: async () => {
      const response = await fetch(`${getProjectUrl(projectSlug)}/judge/default-system-prompt`);
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
