import {API_ROUTES, getProjectApiUrl, urlAsQueryKey} from '../lib/routes.ts';
import { JudgeType } from '../components/Judges/types.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

export function getJudgesQueryKey(projectSlug: string) {
  return urlAsQueryKey(API_ROUTES.getJudges(projectSlug));
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
  const url = API_ROUTES.getJudges(projectSlug ?? '')
  return useQueryWithErrorToast({
    queryKey: getJudgesQueryKey(projectSlug ?? ''),
    queryFn: async () => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch judges');
      }
      const result: Judge[] = await response.json();
      return result;
    },
    enabled: projectSlug != null,
    errorMessage: 'Failed to fetch judges',
  });
}
