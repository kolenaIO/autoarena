import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { useQueryWithErrorToast } from './useQueryWithErrorToast.ts';
import { useRoutes } from './useRoutes.ts';

export type Project = {
  slug: string;
  filename: string;
  filepath: string;
};

export function useProjects() {
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
  return useQueryWithErrorToast({
    queryKey: urlAsQueryKey(apiRoutes.getProjects()),
    queryFn: async () => {
      const response = await apiFetch(apiRoutes.getProjects());
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      const result: Project[] = await response.json();
      return result;
    },
    errorMessage: 'Failed to fetch projects',
  });
}
