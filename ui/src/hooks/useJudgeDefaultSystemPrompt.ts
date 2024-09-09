import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '../lib/baseRoutes.ts';

const JUDGE_DEFAULT_SYSTEM_PROMPT_ENDPOINT = `${BASE_API_URL}/judge/default-system-prompt`;

function getJudgeDefaultSystemPromptQueryKey() {
  return [JUDGE_DEFAULT_SYSTEM_PROMPT_ENDPOINT];
}

export function useJudgeDefaultSystemPrompt() {
  return useQuery({
    queryKey: getJudgeDefaultSystemPromptQueryKey(),
    queryFn: async () => {
      const response = await fetch(JUDGE_DEFAULT_SYSTEM_PROMPT_ENDPOINT);
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
