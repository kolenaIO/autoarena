import { useQuery } from '@tanstack/react-query';
import { JudgeType } from '../components/Judges/types.ts';
import { BASE_API_URL } from '../components/paths.ts';

const CAN_ACCESS_JUDGE_TYPE_ENDPOINT = `${BASE_API_URL}/judge`;

function getCanAccessJudgeTypeQueryKey(judgeType?: JudgeType) {
  return [CAN_ACCESS_JUDGE_TYPE_ENDPOINT, judgeType, 'can-access'];
}

export function useCanAccessJudgeType(judgeType?: JudgeType) {
  return useQuery({
    queryKey: getCanAccessJudgeTypeQueryKey(judgeType),
    queryFn: async () => {
      const url = `${CAN_ACCESS_JUDGE_TYPE_ENDPOINT}/${judgeType}/can-access`;
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
