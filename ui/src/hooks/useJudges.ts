import { getProjectUrl } from '../lib/routes.ts';
import { JudgeType } from '../components/Judges/types.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

export function getJudgesQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/judges'];
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
  n_votes: number;
};

export function useJudges(projectSlug: string | undefined) {
  return useQueryWithErrorToast({
    queryKey: getJudgesQueryKey(projectSlug ?? ''),
    queryFn: async () => {
      const url = `${getProjectUrl(projectSlug ?? '')}/judges`;
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
