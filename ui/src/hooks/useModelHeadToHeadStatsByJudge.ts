import { useMemo } from 'react';
import { useModelHeadToHeadStats } from './useModelHeadToHeadStats.ts';

type Params = {
  projectSlug: string;
  modelId: number;
  judgeId?: number;
};
export function useModelHeadToHeadStatsByJudge({ projectSlug, modelId, judgeId }: Params) {
  const { data: headToHeadStats, ...query } = useModelHeadToHeadStats({ projectSlug, modelId });

  const filteredByJudge = useMemo(
    () =>
      headToHeadStats == null || judgeId == null
        ? headToHeadStats
        : headToHeadStats.filter(({ judge_id }) => judge_id === judgeId),
    [headToHeadStats, judgeId]
  );

  return { data: filteredByJudge, ...query };
}
