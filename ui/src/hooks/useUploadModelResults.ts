import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { getProjectUrl } from '../lib/baseRoutes.ts';
import { getModelsQueryKey, Model } from './useModels.ts';
import { getTasksQueryKey } from './useTasks.ts';

function getUploadModelResultsQueryKey(projectSlug: string) {
  return [`${getProjectUrl(projectSlug)}`, '/model', 'POST'];
}

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<Model, Error, [File, string]>;
};
export function useUploadModelResults({ projectSlug, options }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getUploadModelResultsQueryKey(projectSlug),
    mutationFn: async ([file, modelName]) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('new_model_name', modelName);
      formData.append('project_id', String(projectSlug));
      const response = await fetch(`${getProjectUrl(projectSlug)}/model`, { method: 'POST', body: formData });
      const result: Model = await response.json();
      return result;
    },
    onError: () => {
      notifications.show({
        title: 'Failed to add model',
        message: 'Unable to add model and results',
        color: 'red',
      });
    },
    onSuccess: model => {
      notifications.show({
        title: 'Added model',
        message: `Created model '${model.name}' with ${model.datapoints.toLocaleString()} datapoints`,
        color: 'green',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectSlug) });
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectSlug) });
    },
    ...options,
  });
}
