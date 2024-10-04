import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { zip } from 'ramda';
import { pluralize, urlAsQueryKey, useAppConfig } from '../lib';
import { Model } from './useModels.ts';
import { useAppRoutes } from './useAppRoutes.ts';

type Params = {
  projectSlug: string;
  options?: UseMutationOptions<Model[], Error, [File[], string[]]>;
};
export function useUploadModelResponses({ projectSlug, options }: Params) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
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
        let detail: string;
        try {
          const error: { detail: string } = await response.json();
          detail = error.detail;
        } catch (e) {
          detail = 'Unable to add model responses';
        }
        throw new Error(detail);
      }
      const result: Model[] = await response.json();
      return result;
    },
    onMutate: ([, modelNames]) => {
      notifications.show({
        message: `Uploading responses from ${pluralize(modelNames.length, 'model')}...`,
        loading: true,
        autoClose: false,
        id: 'uploading-model-responses',
      });
    },
    onError: e => {
      notifications.show({
        title: 'Failed to add model responses',
        message: e.toString(),
        color: 'red',
        autoClose: 10_000,
      });
    },
    onSuccess: (models: Model[]) => {
      const title =
        models.length > 1
          ? `Added responses from ${models.length.toLocaleString()} models`
          : 'Added responses from model';
      const nResponses = models.reduce((acc, { n_responses }) => acc + n_responses, 0);
      const maxModelNames = 6;
      const nExtraModels = models.length - maxModelNames;
      const extraModels = nExtraModels > 0 ? ` and ${pluralize(nExtraModels, 'other')}` : '';
      const message =
        models.length > 1
          ? `Created models ${models
              .slice(0, maxModelNames)
              .map(({ name }) => `'${name}'`)
              .join(', ')}${extraModels} with ${nResponses.toLocaleString()} total responses`
          : `Created model '${models[0]?.name}' with ${nResponses.toLocaleString()} responses`;
      notifications.show({ title, message, color: 'green' });
    },
    onSettled: () => {
      notifications.hide('uploading-model-responses');
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getModels(projectSlug)) });
      queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getTasks(projectSlug)) });
    },
    ...options,
  });
}
