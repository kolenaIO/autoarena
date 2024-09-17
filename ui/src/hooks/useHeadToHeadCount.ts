import { useQuery } from '@tanstack/react-query';
import { getProjectApiUrl } from '../lib/routes.ts';

function getHeadToHeadCountQueryKey(projectSlug?: string) {
  return [getProjectApiUrl(projectSlug ?? ''), '/head-to-head', '/count'];
}

export function useHeadToHeadCount(projectSlug?: string) {
  return useQuery({
    queryKey: getHeadToHeadCountQueryKey(projectSlug),
    queryFn: async () => {
      const response = await fetch(`${getProjectApiUrl(projectSlug ?? '')}/head-to-head/count`);
      if (!response.ok) {
        return;
      }
      const result: number = await response.json();
      return result;
    },
    enabled: projectSlug != null,
  });
}
