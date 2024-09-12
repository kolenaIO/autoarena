import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectUrl } from '../lib/routes.ts';
import { taskStatusToColor } from '../lib/tasks.ts/utils.ts';

function getTriggerAutoJudgeQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/judge'];
}

type TriggerAutoJudgeRequest = {
  judge_ids: number[];
  fraction: number;
  skip_existing: boolean;
};

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<void, Error, TriggerAutoJudgeRequest>;
};
export function useTriggerAutoJudge({ projectSlug, options = {} }: Params) {
  return useMutation({
    mutationKey: getTriggerAutoJudgeQueryKey(projectSlug),
    mutationFn: async (request: TriggerAutoJudgeRequest) => {
      const response = await fetch(`${getProjectUrl(projectSlug)}/task/auto-judge`, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to start automated judgement task');
      }
    },
    onSuccess: () => {
      notifications.show({
        title: 'Started automated judgement task',
        message: 'Check the tasks drawer for more information',
        color: taskStatusToColor('in-progress'),
      });
    },
    onError: () => {
      notifications.show({
        title: 'Failed to start automated judgement task',
        color: 'red',
      });
    },
    ...options,
  });
}
