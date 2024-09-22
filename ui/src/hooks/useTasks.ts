import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { useContext } from 'react';
import { AppConfigContext, urlAsQueryKey } from '../lib';
import { useRoutes } from './useRoutes.ts';

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
  const { apiFetch } = useContext(AppConfigContext);
  const { apiRoutes } = useRoutes();
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
