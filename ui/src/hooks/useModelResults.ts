import { useQuery } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';

export function getModelResultsQueryKey(projectSlug: string, modelId: number) {
  return [getProjectUrl(projectSlug), '/model', modelId, '/results'];
}

export type ModelResult = {
  prompt: string;
  response: string;
};

type Params = {
  projectSlug?: string;
  modelId?: number;
};
export function useModelResults({ projectSlug, modelId }: Params) {
  return useQuery({
    queryKey: getModelResultsQueryKey(projectSlug ?? '', modelId ?? -1),
    queryFn: async () => {
      const url = `${getProjectUrl(projectSlug)}/model/${modelId}/results`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: ModelResult[] = await response.json();
      return result;
    },
    enabled: projectSlug != null && modelId != null,
  });
}
