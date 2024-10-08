import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';
import { useAppRoutes } from './useAppRoutes.ts';

export type Task = {
  id: number;
  task_type: 'auto-judge' | 'recompute-leaderboard' | 'fine-tune';
  created: string;
  progress: number;
  status: 'started' | 'in-progress' | 'completed' | 'failed';
  logs: string;
};

type Params = {
  projectSlug?: string;
  options?: Partial<UseQueryOptions<Task[]>>;
};
export function useTasks({ projectSlug, options = {} }: Params) {
  const { apiFetch } = useAppConfig();
  const { apiRoutes } = useAppRoutes();
  const url = apiRoutes.getTasks(projectSlug ?? '');
  return useQuery({
    queryKey: urlAsQueryKey(url),
    queryFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch tasks');
      }
      const result: Task[] = await response.json();
      return result;
    },
    enabled: projectSlug != null,
    ...options,
  });
}
