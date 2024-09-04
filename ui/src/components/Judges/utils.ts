import { Judge } from '../../hooks/useJudges.ts';

export function isEnabledAutoJudge(judge: Judge) {
  return judge.enabled && judge.judge_type !== 'human';
}
