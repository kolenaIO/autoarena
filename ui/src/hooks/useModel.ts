import { useContext, useMemo } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { useModels } from './useModels.ts';

export function useAllModelActionsQueryKey(projectSlug?: string) {
  const { baseApiUrl } = useContext(AppConfigContext);
  return urlAsQueryKey(`${baseApiUrl}/project/${projectSlug ?? ''}/model`, undefined);
}

export function useModel(projectSlug?: string, modelId?: number) {
  const { data: models, ...query } = useModels(projectSlug);
  const model = useMemo(() => (models ?? []).find(({ id }) => id === modelId), [models, modelId]);
  return { data: model, ...query };
}
