import { useQuery } from '@tanstack/react-query';
import { JudgeType } from '../components/Judges/types.ts';
import { getProjectApiUrl } from '../lib/routes.ts';

function getCanAccessJudgeTypeQueryKey(projectSlug: string, judgeType?: JudgeType) {
  return [getProjectApiUrl(projectSlug), '/judge', judgeType, 'can-access'];
}

type Params = {
  projectSlug: string;
  judgeType?: JudgeType;
};
export function useCanAccessJudgeType({ projectSlug, judgeType }: Params) {
  return useQuery({
    queryKey: getCanAccessJudgeTypeQueryKey(projectSlug, judgeType),
    queryFn: async () => {
      const url = `${getProjectApiUrl(projectSlug)}/judge/${judgeType}/can-access`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: boolean = await response.json();
      return result;
    },
    enabled: judgeType != null,
  });
}
