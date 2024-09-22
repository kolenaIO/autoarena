import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { JudgeType } from '../components';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { Judge } from './useJudges.ts';
import { useRoutes } from './useRoutes.ts';

type CreateJudgeRequest = {
  judge_type: JudgeType;
  name: string;
  model_name: string;
  system_prompt: string;
  description: string;
};

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<Judge, Error, CreateJudgeRequest>;
};
export function useCreateJudge({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.createJudge(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'POST'),
    mutationFn: async (request: CreateJudgeRequest) => {
      const response = await apiFetch(url, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error('Failed to create automated judge');
      }
      const result: Judge = await response.json();
      return result;
    },
    onSuccess: judge => {
      notifications.show({
        title: 'Judge created',
        message: `Created automated judge '${judge.name}'`,
        color: 'green',
      });
    },
    onError: () => {
      notifications.show({
        message: 'Failed to create automated judge',
        color: 'red',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getJudges(projectSlug)) });
    },
    ...options,
  });
}
