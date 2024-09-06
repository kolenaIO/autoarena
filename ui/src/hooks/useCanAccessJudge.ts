import { useQuery } from '@tanstack/react-query';
import { JudgeType } from '../components/Judges/types.ts';
import { BASE_API_URL } from '../components/paths.ts';
import { Judge } from './useJudges.ts';

const CAN_ACCESS_JUDGE_TYPE_ENDPOINT = `${BASE_API_URL}/judge`;

function getCanAccessJudgeTypeQueryKey(judgeType: JudgeType | undefined, judge: Judge | undefined) {
  return [CAN_ACCESS_JUDGE_TYPE_ENDPOINT, judgeType, 'can-access', judge];
}

type Params = {
  judgeType?: JudgeType;
  judge?: Judge;
};
export function useCanAccessJudge({ judgeType, judge }: Params) {
  return useQuery({
    queryKey: getCanAccessJudgeTypeQueryKey(judgeType, judge),
    queryFn: async () => {
      const url = `${CAN_ACCESS_JUDGE_TYPE_ENDPOINT}/${judgeType ?? judge?.judge_type}/can-access`;
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
