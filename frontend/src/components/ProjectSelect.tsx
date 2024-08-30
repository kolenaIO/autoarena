import { Select } from '@mantine/core';
import { useMemo } from 'react';
import { useProjects } from '../hooks/useProjects.ts';
import { useUrlState } from '../hooks/useUrlState.ts';

export function ProjectSelect() {
  const { projectId, setProjectId } = useUrlState();
  const { data: projects } = useProjects();
  const allProjectNames = useMemo(() => (projects ?? []).map(({ name }) => name), [projects]);
  const currentProject = useMemo(() => projects?.find(({ id }) => id === projectId), [projects, projectId]);

  function handleSelectProject(projectName: string | null) {
    setProjectId(projects?.find(({ name }) => name === projectName)?.id ?? null);
  }

  return (
    <Select
      variant="filled"
      placeholder="Select Project"
      data={allProjectNames}
      value={currentProject?.name}
      onChange={handleSelectProject}
      disabled={allProjectNames.length < 1}
    />
  );
}
