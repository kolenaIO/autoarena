import { useMemo } from 'react';
import { useProjects } from './useProjects.ts';

export function useProject(projectSlug?: string) {
  const { data: projects, ...query } = useProjects();
  const project = useMemo(() => (projects ?? []).find(({ slug }) => slug === projectSlug), [projects, projectSlug]);
  return { data: project, ...query };
}
