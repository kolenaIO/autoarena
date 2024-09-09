import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../lib/baseRoutes.ts';

function getTriggerModelJudgementEndpoint(modelId: number | undefined) {
  return `${BASE_API_URL}/model/${modelId}/judge`;
}

type Params = {
  modelId?: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useTriggerModelJudgement({ modelId, options = {} }: Params) {
  return useMutation({
    mutationKey: [getTriggerModelJudgementEndpoint(modelId)],
    mutationFn: async () => {
      await fetch(getTriggerModelJudgementEndpoint(modelId), { method: 'POST' });
    },
    onSuccess: () => {
      notifications.show({
        title: 'Started model judgement',
        message: 'Check the tasks drawer for more information',
        color: 'orange',
      });
    },
    ...options,
  });
}
