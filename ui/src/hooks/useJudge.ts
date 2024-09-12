import { useMemo } from 'react';
import { useJudges } from './useJudges.ts';

export function useJudge(projectSlug?: string, judgeId?: number) {
  const { data: judges, ...query } = useJudges(projectSlug);
  const judge = useMemo(() => (judges ?? []).find(({ id }) => id === judgeId), [judges, judgeId]);
  return { data: judge, ...query };
}
