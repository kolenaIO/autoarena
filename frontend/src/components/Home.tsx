import { Center, Checkbox, Code, Group, Table, Text, Tooltip } from '@mantine/core';
import { useMemo, useState } from 'react';
import { IconCrown } from '@tabler/icons-react';
import { useModels } from './useModels.ts';

type Props = {
  elo: number;
  qLo: number;
  qHi: number;
  globalLo: number;
  globalHi: number;
};
function EloWidget({ elo, qLo, qHi, globalLo, globalHi }: Props) {
  const range = globalHi - globalLo;
  const pct = (100 * (elo - globalLo)) / range;
  const pctLo = (100 * (qLo - globalLo)) / range;
  const pctHi = (100 * (qHi - globalLo)) / range;
  const height = 12;
  return (
    <div style={{ position: 'relative', width: 200, height }}>
      <div
        style={{
          position: 'absolute',
          background: 'var(--mantine-color-gray-6)',
          left: `calc(${pctLo.toFixed(1)}% - 1px)`,
          borderRadius: 1,
          width: 2,
          height,
        }}
      />
      <div
        style={{
          position: 'absolute',
          background: 'var(--mantine-color-gray-6)',
          left: `calc(${pctHi.toFixed(1)}% - 1px)`,
          borderRadius: 1,
          width: 2,
          height,
        }}
      />
      <Tooltip label={<Text size="sm">{`Elo: ${elo.toFixed(1)}`}</Text>} openDelay={200}>
        <div
          style={{
            position: 'absolute',
            background: 'var(--mantine-color-kolena-8)',
            left: `calc(${pct.toFixed(1)}% - ${(height - 6) / 2}px - 1px)`,
            width: height - 6,
            height: height - 6,
            transform: 'rotate(45deg)',
            margin: 3,
          }}
        />
      </Tooltip>
    </div>
  );
}

export function Home() {
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const { data: models } = useModels();

  const modelsSorted = useMemo(() => (models ?? []).sort((a, b) => b.elo - a.elo), [models]);
  const globalLo = modelsSorted[modelsSorted.length - 1]?.q025 ?? 0;
  const globalHi = modelsSorted[0]?.q975 ?? 0;

  return (
    <Center p="lg">
      <Table stickyHeader striped withTableBorder highlightOnHover horizontalSpacing="xs" maw={1280}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th />
            <Table.Th>Rank</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th />
            {/* <Table.Th>Created</Table.Th> */}
            <Table.Th>Elo</Table.Th>
            <Table.Th>CI 95%</Table.Th>
            <Table.Th>Votes</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {modelsSorted.map((model, i) => (
            <Table.Tr
              key={i}
              bg={selectedRows.includes(model.id) ? 'var(--mantine-color-kolena-light)' : undefined}
              onclick={() => {
                console.log('clicked', model.id);
              }}
            >
              <Table.Td>
                <Checkbox
                  checked={selectedRows.includes(model.id)}
                  onChange={event => {
                    setSelectedRows(
                      event.currentTarget.checked
                        ? [...selectedRows, model.id]
                        : selectedRows.filter(id => id !== model.id)
                    );
                  }}
                />
              </Table.Td>
              <Table.Td>{i + 1}</Table.Td>
              <Table.Td>
                <Group align="center">
                  <Text size="md">{model.name}</Text>
                  {i === 0 && <IconCrown size={18} color="var(--mantine-color-yellow-6)" />}
                </Group>
              </Table.Td>
              {/* <Table.Td>{moment(model.created).format('YYYY-MM-DD (hh:mm A)')}</Table.Td> */}
              <Table.Td>
                <EloWidget elo={model.elo} qLo={model.q025} qHi={model.q975} globalLo={globalLo} globalHi={globalHi} />
              </Table.Td>
              <Table.Td>{model.elo.toFixed(1)}</Table.Td>
              <Table.Td>
                <Code>
                  +{(model.q975 - model.elo).toFixed(0)} / -{(model.elo - model.q025).toFixed(0)}
                </Code>
              </Table.Td>
              <Table.Td>{model.votes}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Center>
  );
}
