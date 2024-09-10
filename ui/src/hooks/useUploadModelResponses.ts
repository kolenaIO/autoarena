import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectUrl } from '../lib/routes.ts';
import { getModelsQueryKey, Model } from './useModels.ts';
import { getTasksQueryKey } from './useTasks.ts';

function getUploadModelResponsesQueryKey(projectSlug: string) {
  return [`${getProjectUrl(projectSlug)}`, '/model', 'POST'];
}

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<Model[], Error, [File[], string[]]>;
};
export function useUploadModelResponses({ projectSlug, options }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getUploadModelResponsesQueryKey(projectSlug),
    mutationFn: async ([files, modelNames]: [File[], string[]]) => {
      const formData = new FormData();
      files.forEach((file, i) => {
        formData.append(file.name, file);
        formData.append(`${file.name}||model_name`, modelNames[i]); // format here is enforced by backend
      });
      const response = await fetch(`${getProjectUrl(projectSlug)}/model`, { method: 'POST', body: formData });
      const result: Model[] = await response.json();
      return result;
    },
    onError: () => {
      notifications.show({
        title: 'Failed to add model responses',
        message: 'Unable to add model responses',
        color: 'red',
      });
    },
    onSuccess: (models: Model[]) => {
      const title =
        models.length > 1
          ? `Added responses from ${models.length.toLocaleString()} models`
          : 'Added responses from model';
      const nResponses = models.reduce((acc, { n_responses }) => acc + n_responses, 0);
      const message =
        models.length > 1
          ? `Created models ${models.map(({ name }) => name).join(', ')} with ${nResponses.toLocaleString()} total responses`
          : `Created model '${models[0]?.name}' with ${nResponses.toLocaleString()} responses`;
      notifications.show({ title, message, color: 'green' });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectSlug) });
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectSlug) });
    },
    ...options,
  });
}
