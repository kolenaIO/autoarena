import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { BASE_API_URL } from '../components/paths.ts';

const TASKS_ENDPOINT = `${BASE_API_URL}/tasks`;

export function getTasksQueryKey(projectId: number) {
  return [TASKS_ENDPOINT, projectId];
}

export type Task = {
  id: number;
  task_type: 'auto-judge' | 'fine-tune' | 'recompute-confidence-intervals';
  created: string;
  progress: number;
  status: string;
};

type Params = {
  projectId: number | undefined;
  options?: Partial<UseQueryOptions<Task[]>>;
};
export function useTasks({ projectId, options = {} }: Params) {
  return useQuery({
    queryKey: getTasksQueryKey(projectId ?? -1),
    queryFn: async () => {
      const url = `${TASKS_ENDPOINT}/${projectId}`;
      const response = await fetch(url);
      if (!response.ok) {
        return;
      }
      const result: Task[] = await response.json();
      return result;
    },
    enabled: projectId != null,
    ...options,
  });
}
