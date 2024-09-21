import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { JudgeType } from '../components';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { useRoutes } from './useRoutes.ts';

export function getJudgesQueryKey(apiRoutes: ReturnType<useRoutes>['apiRoutes'], projectSlug: string) {
  return urlAsQueryKey(apiRoutes.getJudges(projectSlug));
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
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const url = apiRoutes.getJudges(projectSlug ?? '');
  return useQueryWithErrorToast({
    queryKey: getJudgesQueryKey(apiRoutes, projectSlug ?? ''),
    queryFn: async () => {
      const response = await apiFetch(url);
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
