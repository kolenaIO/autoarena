import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { zip } from 'ramda';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { getModelsQueryKey, Model } from './useModels.ts';
import { getTasksQueryKey } from './useTasks.ts';
import { useRoutes } from './useRoutes.ts';

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<Model[], Error, [File[], string[]]>;
};
export function useUploadModelResponses({ projectSlug, options }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  const queryClient = useQueryClient();
  const url = apiRoutes.uploadModelResponses(projectSlug);
  return useMutation({
    mutationKey: urlAsQueryKey(url, 'POST'),
    mutationFn: async ([files, modelNames]: [File[], string[]]) => {
      if (files.length !== modelNames.length) {
        throw new Error(`Invalid request: ${files.length} files and ${modelNames.length} model names provided`);
      }
      const formData = new FormData();
      zip(files, modelNames).forEach(([file, modelName]) => {
        formData.append(file.name, file);
        formData.append(`${file.name}||model_name`, modelName); // format here is enforced by backend
      });
      const response = await apiFetch(url, { method: 'POST', body: formData });
      if (!response.ok) {
        throw new Error('Failed to add model responses');
      }
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
      queryClient.invalidateQueries({ queryKey: getModelsQueryKey(apiRoutes, projectSlug) });
      queryClient.invalidateQueries({ queryKey: getTasksQueryKey(apiRoutes, projectSlug) });
    },
    ...options,
  });
}
