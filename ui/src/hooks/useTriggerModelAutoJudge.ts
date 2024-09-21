import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { taskStatusToColor } from '../lib';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  modelId?: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useTriggerModelAutoJudge({ projectSlug, modelId, options = {} }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
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
