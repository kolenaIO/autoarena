import { useMemo, useState } from 'react';
import { Group, Loader, Paper, Stack, Text, TextInput } from '@mantine/core';
import { IconClick } from '@tabler/icons-react';
import { DataTable, DataTableSortStatus } from 'mantine-datatable';
import { prop, sortBy } from 'ramda';
import { useModels } from '../../hooks/useModels.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { NonIdealState } from '../NonIdealState.tsx';
import { AddModelButton } from '../AddModelButton.tsx';
import { RankedModel } from './types.ts';
import { LEADERBOARD_COLUMNS, LOADING_MODELS } from './columns.tsx';
import { ExpandedModelDetails } from './ExpandedModelDetails.tsx';
import { ExploreSelectedModels } from './ExploreSelectedModels.tsx';

export function Leaderboard() {
  const { projectId = -1 } = useUrlState();
  const [selectedRecords, setSelectedRecords] = useState<RankedModel[]>([]);
  const [filterValue, setFilterValue] = useState('');
  const { data: models, isLoading } = useModels(projectId);
  const [sortStatus, setSortStatus] = useState<DataTableSortStatus<RankedModel>>({
    columnAccessor: 'rank',
    direction: 'asc',
  });

  const selectedIds = useMemo(() => new Set(selectedRecords.map(({ id }) => id)), [selectedRecords]);
  const allModels = isLoading ? LOADING_MODELS : (models ?? []);
  const globalLo = Math.min(...allModels.map(({ elo, q025 }) => Math.min(elo, q025 ?? Infinity)));
  const globalHi = Math.max(...allModels.map(({ elo, q975 }) => Math.max(elo, q975 ?? 0)));
  // TODO: should assign the same rank to models with equal scores
  const modelsRanked = useMemo(
    () =>
      sortBy(prop('elo'))(allModels)
        .reverse()
        .map<RankedModel>((model, i) => ({ ...model, rank: i + 1, globalLo, globalHi })),
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

  return (
    <Stack p="lg" align="center">
      <Group justify="space-between" w={1080} align="flex-end">
        <TextInput
          label="Filter Models"
          placeholder="Enter filter value..."
          value={filterValue}
          onChange={event => setFilterValue(event.currentTarget.value)}
          flex={1}
          disabled={isLoading}
        />
        {/* <Select label="Judge" data={availableJudges} defaultValue={availableJudges[0]} disabled={isLoading} /> */}
        <AddModelButton variant="light" />
      </Group>
      {!isLoading && allModels.length === 0 ? (
        <Stack justify="center">
          <NonIdealState
            IconComponent={IconClick}
            description={
              <Stack>
                <Text>Add a model to the leaderboard</Text>
                <AddModelButton />
              </Stack>
            }
          />
        </Stack>
      ) : (
        <Paper radius="md" pos="relative" withBorder w={1080}>
          <DataTable<RankedModel>
            striped
            withTableBorder={false}
            borderRadius="md"
            horizontalSpacing="xs"
            columns={LEADERBOARD_COLUMNS}
            records={modelRecords}
            idAccessor="id"
            rowExpansion={{
              content: ({ record }) => <ExpandedModelDetails model={record} />,
              // TODO: ideally use default for smooth transition but render is sometimes choppy
              collapseProps: { transitionDuration: 0 },
            }}
            sortStatus={sortStatus}
            onSortStatusChange={setSortStatus}
            fetching={isLoading}
            loaderBackgroundBlur={4}
            customLoader={<NonIdealState icon={<Loader />} description="Crunching leaderboard rankings..." />}
            selectedRecords={selectedRecords}
            onSelectedRecordsChange={setSelectedRecords}
            isRecordSelectable={({ id }) => selectedRecords.length < 2 || selectedIds.has(id)}
            allRecordsSelectionCheckboxProps={{ display: 'none' }}
          />

          {selectedRecords.length > 0 && <ExploreSelectedModels selectedModels={selectedRecords} />}
        </Paper>
      )}
    </Stack>
  );
}
