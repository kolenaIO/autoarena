import { useQuery } from '@tanstack/react-query';
import { JudgeType } from '../components/Judges/types.ts';
import { getProjectUrl } from '../lib/routes.ts';
import { Judge } from './useJudges.ts';

function getCanAccessJudgeTypeQueryKey({ projectSlug, judgeType, judge }: Params) {
  return [getProjectUrl(projectSlug), '/judge', judgeType ?? judge?.judge_type, 'can-access', judge];
}

type Params = {
  projectSlug: string;
  judgeType?: JudgeType;
  judge?: Judge;
};
export function useCanAccessJudge({ projectSlug, judgeType, judge }: Params) {
  return useQuery({
    queryKey: getCanAccessJudgeTypeQueryKey({ projectSlug, judgeType, judge }),
    queryFn: async () => {
      const url = `${getProjectUrl(projectSlug)}/judge/${judgeType ?? judge?.judge_type}/can-access`;
      const init =
        judge != null
          ? { method: 'PUT', body: JSON.stringify(judge), headers: { 'Content-Type': 'application/json' } }
          : undefined;
      const response = await fetch(url, init);
      if (!response.ok) {
        return;
      }
      const result: boolean = await response.json();
      return result;
    },
    enabled: judgeType != null || judge != null,
  });
}
