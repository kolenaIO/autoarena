import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { BASE_API_URL } from '../components/paths.ts';
import { getModelsQueryKey, Model } from './useModels.ts';
import { getTasksQueryKey } from './useTasks.ts';

const UPLOAD_MODEL_RESULTS_ENDPOINT = `${BASE_API_URL}/model`;

function getUploadModelResultsQueryKey(projectId: number) {
  return [UPLOAD_MODEL_RESULTS_ENDPOINT, projectId];
}

type Params = {
  projectId: number;
  options?: UseMutationOptions<Model, Error, [File, string]>;
};
export function useUploadModelResults({ projectId, options }: Params) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: getUploadModelResultsQueryKey(projectId),
    mutationFn: async ([file, modelName]) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('new_model_name', modelName);
      formData.append('project_id', String(projectId));
      const response = await fetch(UPLOAD_MODEL_RESULTS_ENDPOINT, { method: 'POST', body: formData });
      const result: Model = await response.json();
      return result;
    },
    onSuccess: model => {
      notifications.show({
        title: 'Added model',
        message: `Created model '${model.name}' with ${model.datapoints.toLocaleString()} datapoints.`,
        color: 'green.6',
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(projectId) });
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(projectId) });
    },
    ...options,
  });
}
