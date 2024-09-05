import { Select } from '@mantine/core';
import { useMemo } from 'react';
import { useJudges } from '../../hooks/useJudges.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';

export function JudgeSelect() {
  const { projectId, judgeId, setJudgeId } = useUrlState();
  const { data: judges, isLoading: isLoadingJudges } = useJudges(projectId);

  const judgeIdByName: { [name: string]: number } = useMemo(
    () => Object.fromEntries((judges ?? []).map(({ id, name }) => [name, id])),
    [judges]
  );
  const judgeNameById: { [id: number]: string } = useMemo(
    () => Object.fromEntries((judges ?? []).map(({ id, name }) => [id, name])),
    [judges]
  );
  const availableJudges = useMemo(() => (judges ?? []).map(({ name }) => name), [judges]);
  const currentJudgeName = judgeNameById[judgeId ?? -1] ?? null;

  return (
    <Select
      label="Judge"
      w={250}
      data={availableJudges}
      value={currentJudgeName}
      onChange={name => setJudgeId(name != null ? judgeIdByName[name] : undefined)}
      disabled={isLoadingJudges}
      placeholder="Showing votes from all judges"
      clearable
    />
  );
}
