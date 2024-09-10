import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { getProjectUrl } from '../lib/routes.ts';

export function getTasksQueryKey(projectSlug: string) {
  return [getProjectUrl(projectSlug), '/tasks'];
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
  return useQuery({
    queryKey: getTasksQueryKey(projectSlug ?? ''),
    queryFn: async () => {
      const url = `${getProjectUrl(projectSlug ?? '')}/tasks`;
      const response = await fetch(url);
      if (!response.ok) {
        return [];
      }
      const result: Task[] = await response.json();
      return result;
    },
    enabled: projectSlug != null,
    ...options,
  });
}
