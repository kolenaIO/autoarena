import { useMemo, useState } from 'react';
import { Group, Loader, Paper, Select, Stack, TextInput } from '@mantine/core';
import { DataTable, DataTableSortStatus } from 'mantine-datatable';
import { prop, sortBy } from 'ramda';
import { useModels } from '../../hooks/useModels.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { NonIdealState } from '../NonIdealState.tsx';
import { AddModelButton } from '../AddModelButton.tsx';
import { OnboardingTimeline } from '../OnboardingTimeline.tsx';
import { useOnboardingGuideDismissed } from '../../hooks/useOnboardingGuideDismissed.ts';
import { useJudges } from '../../hooks/useJudges.ts';
import { useModelsRankedByJudge } from '../../hooks/useModelsRankedByJudge.ts';
import { RankedModel } from './types.ts';
import { LEADERBOARD_COLUMNS, LOADING_MODELS } from './columns.tsx';
import { ExpandedModelDetails } from './ExpandedModelDetails.tsx';
import { ExploreSelectedModels } from './ExploreSelectedModels.tsx';
import { LeaderboardSettings } from './LeaderboardSettings.tsx';
import { rankBy } from './utils.ts';

export function Leaderboard() {
  const { projectId } = useUrlState();
  const [selectedRecords, setSelectedRecords] = useState<RankedModel[]>([]);
  const [filterValue, setFilterValue] = useState('');
  const { data: models, isLoading: isLoadingModels } = useModels(projectId);
  const { data: judges, isLoading: isLoadingJudges } = useJudges(projectId);
  const [onboardingGuideDismissed] = useOnboardingGuideDismissed(projectId);
  const [sortStatus, setSortStatus] = useState<DataTableSortStatus<RankedModel>>({
    columnAccessor: 'rank',
    direction: 'asc',
  });

  const [selectedJudge, setSelectedJudge] = useState('All');
  const availableJudges = useMemo(() => ['All', ...(judges ?? []).map(({ name }) => name)], [judges]);
  const judgeIdByName: { [name: string]: number } = useMemo(
    () => Object.fromEntries((judges ?? []).map(({ id, name }) => [name, id])),
    [judges]
  );
  const { data: modelsRankedByJudge, isLoading: isLoadingModelsRankedByJudge } = useModelsRankedByJudge(
    projectId,
    judgeIdByName[selectedJudge]
  );

  const selectedIds = useMemo(() => new Set(selectedRecords.map(({ id }) => id)), [selectedRecords]);
  const allModels = isLoadingModels ? LOADING_MODELS : (modelsRankedByJudge ?? models ?? []);
  const globalLo = Math.min(...allModels.map(({ elo, q025 }) => Math.min(elo, q025 ?? Infinity)));
  const globalHi = Math.max(...allModels.map(({ elo, q975 }) => Math.max(elo, q975 ?? 0)));
  // TODO: should assign the same rank to models with equal scores
  const modelsRanked = useMemo(
    () => rankBy('elo', allModels, 'desc').map<RankedModel>(model => ({ ...model, globalLo, globalHi })),
    [allModels, globalLo, globalHi]
  );
  const modelsSorted = useMemo(() => {
    // @ts-expect-error annoying ramda type issues with prop(sortStatus.columnAccessor)
    const sorted = sortBy<RankedModel>(prop(sortStatus.columnAccessor))(modelsRanked);
    return sortStatus.direction === 'desc' ? sorted.reverse() : sorted;
  }, [modelsRanked, sortStatus]);
  const modelRecords = useMemo(
    () =>
      modelsSorted.filter(
        ({ id, name }) => selectedIds.has(id) || name.toLowerCase().includes(filterValue.toLowerCase())
      ),
    [modelsSorted, filterValue, selectedRecords]
  );

  return onboardingGuideDismissed || isLoadingModels || allModels.length > 0 ? (
    <Stack p="lg" align="center">
      <Group justify="space-between" w={1080} align="flex-end">
        <TextInput
          label="Filter Models"
          placeholder="Enter filter value..."
          value={filterValue}
          onChange={event => setFilterValue(event.currentTarget.value)}
          flex={1}
          disabled={isLoadingModels}
        />
        <Select
          label="Judge"
          data={availableJudges}
          defaultValue={availableJudges[0]}
          value={selectedJudge}
          onChange={setSelectedJudge}
          disabled={isLoadingJudges}
          allowDeselect={false}
          rightSection={isLoadingModelsRankedByJudge ? <Loader size={14} /> : undefined}
        />
        <LeaderboardSettings />
        <AddModelButton variant="light" />
      </Group>

      <Paper radius="md" pos="relative" withBorder w={1080}>
        <DataTable<RankedModel>
          striped
          withTableBorder={false}
          borderRadius="md"
          horizontalSpacing="xs"
          minHeight={modelRecords.length === 0 ? 180 : undefined}
          columns={LEADERBOARD_COLUMNS}
          highlightOnHover
          records={modelRecords}
          idAccessor="id"
          rowExpansion={{
            content: ({ record }) => <ExpandedModelDetails model={record} />,
            // NOTE: default smooth transition can be choppy with more than ~20 models, turn it off
            collapseProps: { transitionDuration: 0 },
          }}
          sortStatus={sortStatus}
          onSortStatusChange={setSortStatus}
          fetching={isLoadingModels || isLoadingModelsRankedByJudge}
          loaderBackgroundBlur={4}
          customLoader={<NonIdealState icon={<Loader />} description="Crunching leaderboard rankings..." />}
          selectedRecords={selectedRecords}
          onSelectedRecordsChange={setSelectedRecords}
          isRecordSelectable={({ id }) => selectedRecords.length < 2 || selectedIds.has(id)}
          allRecordsSelectionCheckboxProps={{ display: 'none' }}
        />

        {selectedRecords.length > 0 && <ExploreSelectedModels selectedModels={selectedRecords} />}
      </Paper>

      <OnboardingTimeline />
    </Stack>
  ) : (
    <Stack p="lg" align="center" justify="center" h="calc(100vh - 58px)">
      <OnboardingTimeline />
    </Stack>
  );
}
