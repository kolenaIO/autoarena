import { useQuery } from '@tanstack/react-query';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { useRoutes } from './useRoutes.ts';

export type ModelResponse = {
  prompt: string;
  response: string;
};

type Params = {
  projectSlug?: string;
  modelId?: number;
};
export function useModelResponses({ projectSlug, modelId }: Params) {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
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
