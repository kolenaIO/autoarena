import { useQuery } from '@tanstack/react-query';
import { useContext } from 'react';
import { JudgeType } from '../components';
import { AppConfigContext } from '../lib';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  judgeType?: JudgeType;
};
export function useCanAccessJudgeType({ projectSlug, judgeType }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes, asQueryKey } = useRoutes();
  const url = apiRoutes.checkCanAccess(projectSlug, judgeType ?? 'unrecognized');
  return useQuery({
    queryKey: asQueryKey(url),
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
