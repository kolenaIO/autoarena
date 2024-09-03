import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { JudgeType } from '../components/Judges/types.ts';
import { BASE_API_URL } from '../components/paths.ts';
import { getJudgesQueryKey, Judge } from './useJudges.ts';

const CREATE_JUDGE_ENDPOINT = `${BASE_API_URL}/judge`;

function getCreateJudgeQueryKey(projectId: number) {
  return [CREATE_JUDGE_ENDPOINT, projectId];
}

type CreateJudgeRequest = {
  project_id: number;
  judge_type: JudgeType;
  name: string;
  description: string;
  // TODO: will need additional information
};

type Params = {
  projectId: number;
  options?: UseMutationOptions<Judge, Error, CreateJudgeRequest>;
};
export function useCreateJudge({ projectId, options = {} }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getCreateJudgeQueryKey(projectId),
    mutationFn: async (request: CreateJudgeRequest) => {
      const response = await fetch(CREATE_JUDGE_ENDPOINT, {
        method: 'POST',
        body: JSON.stringify(request),
        headers: { 'Content-Type': 'application/json' },
      });
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
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getJudgesQueryKey(projectId) });
    },
    ...options,
  });
}
