import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { taskStatusToColor } from '../lib';
import { useAppRoutes } from './useAppRoutes.ts';

type Params = {
  projectSlug: string;
  modelId?: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useTriggerModelAutoJudge({ projectSlug, modelId, options = {} }: Params) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.triggerModelAutoJudge(projectSlug, modelId ?? -1);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'POST'),
    mutationFn: async () => {
      const response = await apiFetch(url, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to start automated judgement for model');
      }
    },
    onSuccess: () => {
      notifications.show({
        title: 'Started model judgement',
        message: 'Check the tasks drawer for more information',
        color: taskStatusToColor('in-progress'),
      });
    },
    ...options,
  });
}
