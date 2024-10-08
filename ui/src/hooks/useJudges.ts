import { urlAsQueryKey, useAppConfig } from '../lib';
import { JudgeType } from '../components';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { useAppRoutes } from './useAppRoutes.ts';

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
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.getJudges(projectSlug ?? '');
  return useQueryWithErrorToast({
    queryKey: urlAsQueryKey(url),
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
