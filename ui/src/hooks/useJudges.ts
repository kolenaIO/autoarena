import { BASE_API_URL } from '../components/paths.ts';
import { JudgeType } from '../components/Judges/types.ts';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';

const JUDGES_ENDPOINT = `${BASE_API_URL}/judges`;

export function getJudgesQueryKey(projectId: number) {
  return [JUDGES_ENDPOINT, projectId];
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

export function useJudges(projectId: number | undefined) {
  return useQueryWithErrorToast({
    queryKey: getJudgesQueryKey(projectId ?? -1),
    queryFn: async () => {
      const url = `${JUDGES_ENDPOINT}/${projectId}`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: Judge[] = await response.json();
      return result;
    },
    enabled: projectId != null,
    errorMessage: 'Failed to fetch judges',
  });
}
