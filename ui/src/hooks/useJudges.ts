import { BASE_API_URL } from '../lib/baseRoutes.ts';
import { JudgeType } from '../components/Judges/types.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

const JUDGES_ENDPOINT = `${BASE_API_URL}/judges`;

export function getJudgesQueryKey(projectSlug: string) {
  return [JUDGES_ENDPOINT, projectSlug];
}

export type Judge = {
  id: number;
  judge_type: JudgeType;
  created: string;
  name: string;
  model_name: string | null;
  system_prompt: string | null;
  description: string;
  enabled: boolean;
  votes: number;
};

export function useJudges(projectSlug: string | undefined) {
  return useQueryWithErrorToast({
    queryKey: getJudgesQueryKey(projectSlug ?? ''),
    queryFn: async () => {
      const url = `${JUDGES_ENDPOINT}/${projectSlug}`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: Judge[] = await response.json();
      return result;
    },
    enabled: projectSlug != null,
    errorMessage: 'Failed to fetch judges',
  });
}
