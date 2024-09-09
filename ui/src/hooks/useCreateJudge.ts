import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { JudgeType } from '../components/Judges/types.ts';
import { getProjectUrl } from '../lib/baseRoutes.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';

function getCreateJudgeQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/judge', 'POST'];
}

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
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getCreateJudgeQueryKey(projectSlug),
    mutationFn: async (request: CreateJudgeRequest) => {
      const response = await fetch(`${getProjectUrl(projectSlug)}/judge`, {
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
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectSlug) });
    },
    ...options,
  });
}
