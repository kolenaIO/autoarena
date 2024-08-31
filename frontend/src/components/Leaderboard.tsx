import { useMemo, useState } from 'react';
import {
  Button,
  Card,
  Checkbox,
  Code,
  Group,
  Loader,
  LoadingOverlay,
  Paper,
  Portal,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Tooltip,
} from '@mantine/core';
import { IconClick, IconCrown } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import { Model, useModels } from '../hooks/useModels.ts';
import { useUrlState } from '../hooks/useUrlState.ts';
import { useJudges } from '../hooks/useJudges.ts';
import { EloWidget } from './EloWidget.tsx';
import { NonIdealState } from './NonIdealState.tsx';
import { AddModel } from './AddModel.tsx';

const LOADING_MODELS: Model[] = Array(16)
  .fill(null)
  .map((_, i) => {
    const elo = 1000 + (0.5 - Math.random()) * 1000;
    return {
      id: i,
      name: uuidv4().substring(0, 10 + Math.random() * 25),
      created: 'TODO',
      elo,
      q025: elo - Math.random() * 50,
      q975: elo + Math.random() * 50,
      datapoints: 500 + Math.random() * 1000,
      votes: Math.floor(elo),
    };
  })
  .sort((a, b) => b.elo - a.elo);

export function Leaderboard() {
  const { projectId = -1 } = useUrlState();
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [filterValue, setFilterValue] = useState('');
  const { data: models, isLoading } = useModels(projectId);
  const { data: judges } = useJudges(projectId);
  const navigate = useNavigate();

  const availableJudges = useMemo(() => ['All', ...(judges ?? []).map(({ name }) => name)], [judges]);

  const allModels = isLoading ? LOADING_MODELS : (models ?? []);
  const modelsSorted = useMemo(() => allModels.sort((a, b) => b.elo - a.elo), [allModels]);
  // TODO: should assign the same rank to models with equal scores
  const modelsRanked = useMemo(() => modelsSorted.map((model, i) => ({ ...model, rank: i + 1 })), [modelsSorted]);
  const modelsFiltered = useMemo(
    () =>
      modelsRanked.filter(
        ({ id, name }) => selectedRows.includes(id) || name.toLowerCase().includes(filterValue.toLowerCase())
      ),
    [modelsRanked, filterValue, selectedRows]
  );
  const globalLo = Math.min(...allModels.map(({ elo, q025 }) => Math.min(elo, q025 ?? Infinity)));
  const globalHi = Math.max(...allModels.map(({ elo, q975 }) => Math.max(elo, q975 ?? 0)));

  function getModelById(modelId: number) {
    return (models ?? []).find(({ id }) => id === modelId);
  }

  function handleGoCompare() {
    const modelA = getModelById(selectedRows[0] ?? -1);
    const modelB = getModelById(selectedRows[1] ?? -1);
    if (modelA == null || modelB == null) {
      return;
    }
    const params = new URLSearchParams({ modelA: String(modelA.id), modelB: String(modelB.id) });
    navigate(`/project/${projectId}/compare?${params}`);
  }

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
        <Select label="Judge" data={availableJudges} defaultValue={availableJudges[0]} disabled={isLoading} />
        <AddModel variant="light" />
      </Group>
      {!isLoading && allModels.length === 0 ? (
        <Stack justify="center">
          <NonIdealState
            IconComponent={IconClick}
            description={
              <Stack>
                <Text>Add a model to the leaderboard</Text>
                <AddModel />
              </Stack>
            }
          />
        </Stack>
      ) : (
        <Paper radius="md" pos="relative" withBorder w={1080}>
          <Table striped highlightOnHover horizontalSpacing="xs">
            {selectedRows.length > 0 && (
              <Portal>
                <Card
                  withBorder
                  shadow="md"
                  style={{
                    position: 'fixed',
                    zIndex: 10,
                    width: 400,
                    bottom: 24,
                    right: 'calc(50% - 200px)',
                    left: 'calc(50% - 200px)',
                  }}
                >
                  <Stack>
                    <Text>
                      Compare{' '}
                      <Text span inherit c="blue.6">
                        {getModelById(selectedRows[0] ?? -1)?.name}
                      </Text>{' '}
                      with{' '}
                      {selectedRows.length < 2 ? (
                        <Text span inherit c="dimmed" fs="italic">
                          Select Row
                        </Text>
                      ) : (
                        <Text span inherit c="orange.6">
                          {getModelById(selectedRows[1] ?? -1)?.name}
                        </Text>
                      )}
                      :
                    </Text>
                    <Button disabled={selectedRows.length < 2} onClick={handleGoCompare}>
                      Go
                    </Button>
                  </Stack>
                </Card>
              </Portal>
            )}
            <LoadingOverlay
              visible={isLoading}
              zIndex={1000}
              overlayProps={{ radius: 'md', blur: 4 }}
              loaderProps={{
                children: <NonIdealState icon={<Loader />} description="Crunching leaderboard rankings..." />,
              }}
            />
            <Table.Thead style={{ top: 56 /* TODO: parametrize, this is the header height */ }}>
              <Table.Tr>
                <Table.Th />
                <Table.Th>Rank</Table.Th>
                <Table.Th>Name</Table.Th>
                <Table.Th />
                {/* <Table.Th>Created</Table.Th> */}
                <Table.Th>Elo</Table.Th>
                <Table.Th>CI 95%</Table.Th>
                <Table.Th># Datapoints</Table.Th>
                <Table.Th># Votes</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {modelsFiltered.map((model, i) => (
                <Table.Tr
                  key={i}
                  bg={selectedRows.includes(model.id) ? 'var(--mantine-color-kolena-light)' : undefined}
                >
                  <Table.Td>
                    <Checkbox
                      checked={selectedRows.includes(model.id)}
                      disabled={selectedRows.length >= 2 && !selectedRows.includes(model.id)}
                      onChange={event => {
                        setSelectedRows(
                          event.currentTarget.checked
                            ? [...selectedRows, model.id]
                            : selectedRows.filter(id => id !== model.id)
                        );
                      }}
                    />
                  </Table.Td>
                  <Table.Td>{model.elo > 0 ? model.rank : <Text c="dimmed">-</Text>}</Table.Td>
                  <Table.Td>
                    <Group align="center">
                      {model.votes > 0 ? (
                        <Text size="md">{model.name}</Text>
                      ) : (
                        <Tooltip openDelay={200} label="No votes yet">
                          <Text size="md" c="dimmed" fs="italic">
                            {model.name}
                          </Text>
                        </Tooltip>
                      )}
                      {i === 0 && model.votes > 0 && (
                        <Tooltip openDelay={200} label="Champion">
                          <IconCrown size={18} color="var(--mantine-color-yellow-6)" />
                        </Tooltip>
                      )}
                    </Group>
                  </Table.Td>
                  {/* <Table.Td>{moment(model.created).format('YYYY-MM-DD (hh:mm A)')}</Table.Td> */}
                  <Table.Td>
                    {model.q025 != null && model.q975 != null && (
                      <EloWidget
                        elo={model.elo}
                        qLo={model.q025}
                        qHi={model.q975}
                        globalLo={globalLo}
                        globalHi={globalHi}
                      />
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Code>{model.elo?.toFixed(1)}</Code>
                  </Table.Td>
                  <Table.Td>
                    {model.elo != null && model.q025 != null && model.q975 != null && (
                      <Code>
                        +{(model.q975 - model.elo).toFixed(0)} / -{(model.elo - model.q025).toFixed(0)}
                      </Code>
                    )}
                  </Table.Td>
                  <Table.Td>{model.datapoints.toLocaleString()}</Table.Td>
                  <Table.Td>{model.votes.toLocaleString()}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Paper>
      )}
    </Stack>
  );
}
