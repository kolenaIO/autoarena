import { Group, Select } from '@mantine/core';
import { useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getProjectsQueryKey, useProjects, useUrlState, useProject } from '../hooks';
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
