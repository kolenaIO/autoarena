import { Select } from '@mantine/core';
import { useMemo } from 'react';
import { useProjects } from '../hooks/useProjects.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useProject } from '../hooks/useProject.ts';

export function ProjectSelect() {
  const { projectId, setProjectId } = useUrlState();
  const { data: projects } = useProjects();
  const { data: currentProject } = useProject(projectId);
  const allProjectNames = useMemo(() => (projects ?? []).map(({ name }) => name), [projects]);

  function handleSelectProject(projectName: string | null) {
    setProjectId(projects?.find(({ name }) => name === projectName)?.id ?? null);
  }

  return (
    <Select
      variant="filled"
      placeholder="Select Project"
      data={allProjectNames}
      value={currentProject?.name ?? null}
      onChange={handleSelectProject}
      disabled={allProjectNames.length < 1}
    />
  );
}
