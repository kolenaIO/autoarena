import { useEffect, useMemo, useState } from 'react';
import { prop, reverse, sortBy } from 'ramda';
import { Code, Paper } from '@mantine/core';
import { DataTable, DataTableColumn, DataTableSortStatus } from 'mantine-datatable';
import { useNavigate } from 'react-router-dom';
import { ModelHeadToHeadStats, useUrlState, useModelHeadToHeadStatsByJudge, usePagination } from '../../hooks';
import { ROUTES } from '../../lib';

type H2hStatsRecord = ModelHeadToHeadStats & {
  unique_id: string;
  count_total: number;
  win_percentage: number;
  loss_percentage: number;
  sort_slug: string;
};

const HEAD_TO_HEAD_COLUMNS: DataTableColumn<H2hStatsRecord>[] = [
  { accessor: 'judge_name', title: 'Judge', sortable: true },
  { accessor: 'other_model_name', title: 'Opponent Model', sortable: true },
  { accessor: 'count_total', title: '# Head-to-Heads', sortable: true },
  {
    accessor: 'count_wins',
    title: 'Record (Win - Loss - Tie)',
    render: ({ count_wins, count_losses, count_ties }) => (
      <Code>
        {count_wins.toLocaleString()} - {count_losses.toLocaleString()} - {count_ties.toLocaleString()}
      </Code>
    ),
  },
  {
    accessor: 'win_percentage',
    title: 'Win %',
    sortable: true,
    render: ({ win_percentage }) => `${win_percentage.toFixed(1)}%`,
  },
  {
    accessor: 'loss_percentage',
    title: 'Loss %',
    sortable: true,
    render: ({ loss_percentage }) => `${loss_percentage.toFixed(1)}%`,
  },
];

type Props = {
  modelId: number;
};
export function HeadToHeadStatsTable({ modelId }: Props) {
  const { projectSlug = '', judgeId } = useUrlState();
  const navigate = useNavigate();
  const { data: headToHeadStats, isLoading } = useModelHeadToHeadStatsByJudge({ projectSlug, modelId, judgeId });

  const [sortStatus, setSortStatus] = useState<DataTableSortStatus<H2hStatsRecord>>({
    columnAccessor: 'sort_slug',
    direction: 'desc',
  });

  const statsRecords = useMemo(() => {
    const stats = headToHeadStats ?? [];
    const statsHydrated = stats.map<H2hStatsRecord>(s => {
      const countTotal = s.count_wins + s.count_losses + s.count_ties;
      const winPercentage = (s.count_wins / countTotal) * 100;
      const tiePercentage = (s.count_ties / countTotal) * 100;
      return {
        ...s,
        count_total: countTotal,
        win_percentage: winPercentage,
        loss_percentage: (s.count_losses / countTotal) * 100,
        unique_id: `${s.judge_id}-${s.other_model_id}`,
        sort_slug: `${winPercentage.toFixed(5)}-${tiePercentage.toFixed(5)}-${s.other_model_name}`,
      };
    });
    const sortProp = sortStatus.columnAccessor as keyof H2hStatsRecord;
    const statsSorted = sortBy<H2hStatsRecord>(prop(sortProp))(statsHydrated);
    return sortStatus.direction === 'desc' ? reverse<H2hStatsRecord>(statsSorted) : statsSorted;
  }, [headToHeadStats, sortStatus, judgeId]);
  const { pageNumber, setPageNumber, pageSize, pageRecords } = usePagination({
    records: statsRecords,
    withHotkeys: true,
  });

  useEffect(() => {
    setPageNumber(1);
  }, [sortStatus]);

  return (
    <Paper withBorder radius="md">
      <DataTable<H2hStatsRecord>
        striped
        withTableBorder={false}
        borderRadius="md"
        horizontalSpacing="xs"
        columns={HEAD_TO_HEAD_COLUMNS}
        records={pageRecords}
        idAccessor="unique_id"
        sortStatus={sortStatus}
        onSortStatusChange={setSortStatus}
        fetching={isLoading}
        loaderBackgroundBlur={4}
        minHeight={statsRecords.length === 0 ? 180 : undefined}
        highlightOnHover
        onRowClick={({ record: { other_model_id } }) => {
          navigate(`${ROUTES.compare(projectSlug)}?modelA=${modelId}&modelB=${other_model_id}`);
        }}
        page={pageNumber}
        onPageChange={setPageNumber}
        totalRecords={statsRecords.length}
        recordsPerPage={pageSize}
        paginationActiveTextColor="var(--mantine-color-kolena-light-color)"
        paginationActiveBackgroundColor="var(--mantine-color-kolena-light)"
      />
    </Paper>
  );
}
