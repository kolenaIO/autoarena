import { useQuery } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useAppRoutes } from './useAppRoutes.ts';

export type ModelResponse = {
  prompt: string;
  response: string;
};

type Params = {
  projectSlug?: string;
  modelId?: number;
};
export function useModelResponses({ projectSlug, modelId }: Params) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.getModelResponses(projectSlug ?? '', modelId ?? -1);
  return useQuery({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch model responses');
      }
      const result: ModelResponse[] = await response.json();
      return result;
    },
    enabled: projectSlug != null && modelId != null,
  });
}
