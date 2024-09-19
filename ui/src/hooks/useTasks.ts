import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { API_ROUTES, urlAsQueryKey } from '../lib/routes.ts';
import { useApiFetch } from './useApiFetch.ts';

export function getTasksQueryKey(projectSlug: string) {
  return urlAsQueryKey(API_ROUTES.getTasks(projectSlug));
}

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
  const { apiFetch } = useApiFetch();
  const url = API_ROUTES.getTasks(projectSlug ?? '');
  return useQuery({
    queryKey: getTasksQueryKey(projectSlug ?? ''),
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
