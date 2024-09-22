import { Group, Select } from '@mantine/core';
import { useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useProjects, useUrlState, useProject, useAppRoutes } from '../hooks';
import { urlAsQueryKey } from '../lib';
import { CreateProjectButton } from './CreateProjectButton.tsx';

export function ProjectSelect() {
  const { projectSlug, setProjectSlug } = useUrlState();
  const { apiRoutes } = useAppRoutes();
  const queryClient = useQueryClient();
  const { data: projects } = useProjects();
  const { data: currentProject } = useProject(projectSlug);
  const allProjectSlugs = useMemo(() => (projects ?? []).map(({ slug }) => slug), [projects]);

  function handleSelectProject(projectSlug: string | null) {
    setProjectSlug(projectSlug ?? null);
  }

  function handleRefetchProjects() {
    queryClient.invalidateQueries({ queryKey: urlAsQueryKey(apiRoutes.getProjects()) });
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
