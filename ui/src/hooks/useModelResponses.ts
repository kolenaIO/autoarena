import { useQuery } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';

export function getModelResponsesQueryKey(projectSlug: string, modelId: number) {
  return [getProjectUrl(projectSlug), '/model', modelId, '/responses'];
}

export type ModelResponse = {
  prompt: string;
  response: string;
};

type Params = {
  projectSlug?: string;
  modelId?: number;
};
export function useModelResponses({ projectSlug, modelId }: Params) {
  return useQuery({
    queryKey: getModelResponsesQueryKey(projectSlug ?? '', modelId ?? -1),
    queryFn: async () => {
      const url = `${getProjectUrl(projectSlug ?? '')}/model/${modelId}/responses`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: ModelResponse[] = await response.json();
      return result;
    },
    enabled: projectSlug != null && modelId != null,
  });
}
