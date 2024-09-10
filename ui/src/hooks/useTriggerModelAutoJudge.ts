import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectUrl } from '../lib/routes.ts';

function getTriggerModelJudgementQueryKey(projectSlug: string, modelId: number | undefined) {
  return [getProjectUrl(projectSlug), '/model', modelId, '/judge'];
}

type Params = {
  projectSlug: string;
  modelId?: number;
  options?: UseMutationOptions<void, Error, void>;
};
export function useTriggerModelAutoJudge({ projectSlug, modelId, options = {} }: Params) {
  return useMutation({
    mutationKey: getTriggerModelJudgementQueryKey(projectSlug, modelId),
    mutationFn: async () => {
      await fetch(`${getProjectUrl(projectSlug)}/model/${modelId}/judge`, { method: 'POST' });
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
