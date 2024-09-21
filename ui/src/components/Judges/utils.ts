import { Judge } from '../../hooks';

export function isEnabledAutoJudge(judge: Judge) {
  return judge.enabled && judge.judge_type !== 'human';
}
