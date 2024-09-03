import { useMemo } from 'react';
import { useProjects } from './useProjects.ts';

export function useProject(projectId?: number) {
  const { data: projects, ...query } = useProjects();
  const project = useMemo(() => (projects ?? []).find(({ id }) => id === projectId), [projects, projectId]);
  return { data: project, ...query };
}
