import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { taskStatusToColor } from '../lib';
import { useAppRoutes } from './useAppRoutes.ts';

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
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.triggerAutoJudge(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'POST'),
    mutationFn: async (request: TriggerAutoJudgeRequest) => {
      const response = await apiFetch(url, {
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
        message: 'Failed to start automated judgement task',
        color: 'red',
      });
    },
    ...options,
  });
}
