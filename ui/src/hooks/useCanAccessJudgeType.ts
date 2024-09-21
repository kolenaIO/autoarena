import { useQuery } from '@tanstack/react-query';
import { JudgeType } from '../components';
import { API_ROUTES, urlAsQueryKey } from '../lib';
import { useApiFetch } from './useApiFetch.ts';

type Params = {
  projectSlug: string;
  judgeType?: JudgeType;
};
export function useCanAccessJudgeType({ projectSlug, judgeType }: Params) {
  const { apiFetch } = useApiFetch();
  const url = API_ROUTES.checkCanAccess(projectSlug, judgeType ?? 'unrecognized');
  return useQuery({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to check judge type availability');
      }
      const result: boolean = await response.json();
      return result;
    },
    enabled: judgeType != null,
  });
}
