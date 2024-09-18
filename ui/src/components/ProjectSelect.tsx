import { Group, Select } from '@mantine/core';
import { useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getProjectsQueryKey, useProjects } from '../hooks/useProjects.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useProject } from '../hooks/useProject.ts';
import { CreateProjectButton } from './CreateProjectButton.tsx';

export function ProjectSelect() {
  const { projectSlug, setProjectSlug } = useUrlState();
  const queryCilent = useQueryClient();
  const { data: projects } = useProjects();
  const { data: currentProject } = useProject(projectSlug);
  const allProjectSlugs = useMemo(() => (projects ?? []).map(({ slug }) => slug), [projects]);

  function handleSelectProject(projectSlug: string | null) {
    setProjectSlug(projectSlug ?? null);
  }

  function handleRefetchProjects() {
    queryCilent.invalidateQueries({ queryKey: getProjectsQueryKey() });
  }

  // TODO: this can be simplified now that slugs are IDs are strings
  return (
    <Group gap="xs">
      <Select
        placeholder="Select Project"
        size="xs"
        data={allProjectSlugs}
        value={currentProject?.slug ?? null}
        onChange={handleSelectProject}
        disabled={allProjectSlugs.length < 1}
        onDropdownOpen={handleRefetchProjects}
      />
      <CreateProjectButton small />
    </Group>
  );
}
