import { useMemo } from 'react';
import { useModelHeadToHeadStats } from './useModelHeadToHeadStats.ts';

export function useModelHeadToHeadStatsByJudge(modelId: number, judgeId: number | undefined) {
  const { data: headToHeadStats, ...query } = useModelHeadToHeadStats(modelId);

  const filteredByJudge = useMemo(
    () =>
      headToHeadStats == null || judgeId == null
        ? headToHeadStats
        : headToHeadStats.filter(({ judge_id }) => judge_id === judgeId),
    [headToHeadStats, judgeId]
  );

  return { data: filteredByJudge, ...query };
}
