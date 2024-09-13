import { useMemo } from 'react';
import { useModels } from './useModels.ts';

export function useModel(projectSlug?: string, modelId?: number) {
  const { data: models, ...query } = useModels(projectSlug);
  const model = useMemo(() => (models ?? []).find(({ id }) => id === modelId), [models, modelId]);
  return { data: model, ...query };
}
